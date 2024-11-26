import requests
import logging
import json
from Base import Base

format_str = (
    "[%(asctime)s] %(filename)s:%(funcName)s:%(lineno)d - %(levelname)s: %(message)s"
)
logging.basicConfig(level=logging.DEBUG, format=format_str)


class Springer(Base):
    def __init__(self, api_key):
        """
        Initialize the Springer (springernature) API client.
        :param api_key: Your Springer API key
        """
        self.base_url = "https://api.springernature.com/openaccess/json"
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
        Retrieve publications from Springer by author name, with flexible search options.
        :param author_name: The name of the author to search for (full name, initials, etc.)
        :param rows: The number of results to return (default is 10)
        :return: A list of dictionaries containing publication details
        """
        if author_name.strip() == "":
            logging.warning(
                "Received empty string for author name in search query, returning None"
            )
            return None

        # Normalize the author name before querying
        normalized_name = self.normalize_author_name(author_name)

        # Prepare the query parameters
        params = {
            "q": normalized_name,  # Author query (normalized format)
            "p": rows,  # Limit number of results
            "api_key": self.api_key,
        }

        # Send the request to the Springer API
        response = requests.get(self.base_url, params=params)

        if response.status_code != 200:
            logging.error(
                f"Error fetching data from Springer API: {response.status_code}"
            )
            return None

        # Parse the JSON response
        data = response.json()

        # Extract publication records
        publications = []
        for record in data.get("records", []):
            title = record.get("title", "No title available")
            publication_name = record.get("publicationName", "No journal available")
            publication_date = record.get("publicationDate", "No date available")
            content_type = record.get("contentType", "No type available")
            doi = record.get("doi", "No DOI available")

            creators = record.get("creators", [])
            authors = [creator.get("creator", "") for creator in creators]

            if all([title, authors, publication_date, publication_name]):
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
    :param api_key: Springer API key
    :param authors: List of author names to search for (supports full names, initials, etc.)
    :param limit: The number of results to limit for each author (default is 10)
    :return: Dictionary with results for each author
    """
    springer_api = Springer(api_key)
    all_results = {}

    for author in authors:
        print(f"Searching for publications by {author}...")
        if author == "":
            logging.warning("Received empty string for author name, continuing...")
            continue
        try:
            # Get publications for each author, passing the limit (rows) to get_publications_by_author
            publications = springer_api.get_publications_by_author(author, rows=limit)
            all_results[author] = publications
        except Exception as e:
            logging.error(f"Error fetching data for {author}: {e}")

    return all_results


# Example usage:
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

