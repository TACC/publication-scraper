import requests
import json
import logging

from pubscraper.APIClasses.Base import Base
import config

# Set up basic logging
format_str = (
    "[%(asctime)s] %(filename)s:%(funcName)s:%(lineno)d - %(levelname)s: %(message)s"
)
logging.basicConfig(level=logging.DEBUG, format=format_str)


class Elsevier(Base):
    def __init__(self, api_key):
        """
        Initialize the Elsevier API client.
        :param api_key: Your Elsevier API key
        """
        self.base_url = config.ELSEVIER_URL
        self.api_key = api_key

    def standardize_author_name(self, author_name):
        """
        Standardize author names to handle variations like "T C Moore", "Timothy C Moore", and "Timothy C. Moore".
        :param author_name: The name to standardize
        :return: Standardized author name in the format "Timothy C. Moore"
        """
        name_parts = author_name.split()

        # Capitalize each part of the name
        name_parts = [part.capitalize() for part in name_parts]

        # If the author has a middle initial, ensure it is followed by a dot
        if len(name_parts) == 3 and len(name_parts[1]) == 1:
            # Make sure the middle initial is followed by a dot
            middle_name = name_parts[1] + "."
            return f"{name_parts[0]} {middle_name} {name_parts[2]}"
        elif len(name_parts) == 2:  # No middle name, just first and last name
            return f"{name_parts[0]} {name_parts[1]}"
        else:
            # Handle other cases (like middle name fully spelled out)
            return " ".join(name_parts)

    def get_publications_by_author(self, author_name, rows=10):
        """
        Retrieve publications from Elsevier by author name.
        :param author_name: The name of the author to search for
        :param rows: The number of results to return (default is 10)
        :return: A list of dictionaries containing publication details
        """
        if not author_name.strip():
            logging.warning("Received empty string for author name, skipping search.")
            return None

        # Normalize the author name
        normalized_name = self.standardize_author_name(author_name)

        # Prepare the query parameters
        params = {
            "query": f"AUTHOR-NAME({normalized_name})",
            "count": rows,
            "apiKey": self.api_key,
        }

        # Send the request to the Elsevier API
        headers = {"Accept": "application/json"}
        
        # Error handling when interacting with Elsevier APIs, Raises HTTP Error for bad responses
        try:
            response = requests.get(self.base_url, headers=headers, params=params, timeout=10)  
            response.raise_for_status()  
        except requests.exceptions.RequestException as e:
            logging.error(f"Elsevier API Request error: {e}")
            return None
        

        # Log the raw response for debugging
        data = response.json()

        # Extract publication records
        publications = []
        for record in data.get("search-results", {}).get("entry", []):
            # Get basic publication details
            title = record.get("dc:title", "No title available")
            publication_name = record.get(
                "prism:publicationName", "No journal available"
            )
            publication_date = record.get("prism:coverDate", "No date available")
            content_type = record.get("subtypeDescription", "No type available")
            doi = record.get("prism:doi", "No DOI available")

            # Get authors (ensure multiple authors are captured)
            authors = []
            if "author" in record:
                for author in record["author"]:
                    author_name = author.get("authname", "")
                    if author_name:
                        authors.append(author_name)
            elif "dc:creator" in record:
                authors.append(record["dc:creator"])

            # Create a dictionary with the relevant information
            publication = {
                "doi": doi,
                "journal": publication_name,
                "content_type": content_type,
                "publication_date": publication_date,
                "title": title,
                "authors": ", ".join(authors),
            }
            publications.append(publication)

        return publications


def search_multiple_authors(api_key, authors, limit=10):
    """
    Search for publications by multiple authors.
    :param api_key: Elsevier API key
    :param authors: List of author names to search for
    :return: Dictionary with results for each author
    """
    elsevier_api = Elsevier(api_key)
    all_results = {}  # Dictionary to hold results for all authors

    for author in authors:
        print(f"Searching for publications by {author}...")
        if author == "":
            logging.warning("Received empty string for author name, continuing...")
            continue
        try:
            # Get publications for each author
            publications = elsevier_api.get_publications_by_author(author, rows=limit)
            all_results[author] = publications if publications else []
        except Exception as e:
            logging.error(f"Error fetching data for {author}: {e}")
            all_results[author] = []  # On error, return an empty list for the author

    return all_results


if __name__ == "__main__":
    # Get API key
    api_key = ""

    # Input: list of author names (comma-separated input)
    author_names = input("Enter author names (comma-separated): ").split(",")

    # Strip any leading/trailing whitespace
    author_names = [name.strip() for name in author_names]

    # Get results for all authors
    results = search_multiple_authors(api_key, author_names)

    # Output the results in JSON format
    print(json.dumps(results, indent=4))
