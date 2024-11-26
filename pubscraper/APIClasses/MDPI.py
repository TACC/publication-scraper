import requests
import logging
import json

from pubscraper.APIClasses.Base import Base
import config

format_str = (
    "[%(asctime)s] %(filename)s:%(funcName)s:%(lineno)d - %(levelname)s: %(message)s"
)
logging.basicConfig(level=logging.DEBUG, format=format_str)


class MDPI(Base):
    def __init__(self, api_key=None):
        """api
        Initialize the MDPI API client.
        :param api_key: Your MDPI API key (if required, can be None for public access).
        """
        self.base_url = config.MDPI_URL
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
        Retrieve publications from MDPI by author name.
        :param author_name: The name of the author to search for.
        :param rows: The number of results to return (default is 10).
        :return: A list of dictionaries containing publication details.
        """
        if not author_name.strip():
            logging.warning(
                "Received empty string for author name in search query, returning None"
            )
            return None

        # Normalize the author name before querying
        normalized_name = self.standardize_author_name(author_name)

        # Prepare the query parameters
        params = {
            "author": normalized_name,  # Query for author
            "rows": rows,  # Limit the number of results
        }

        if self.api_key:
            params["api_key"] = self.api_key

        # Send the request to the MDPI API
        response = requests.get(self.base_url, params=params)

        if response.status_code != 200:
            logging.error(f"Error fetching data from MDPI API: {response.status_code}")
            return None

        # Parse the JSON response
        data = response.json()

        # Extract publication records
        publications = []
        for article in data.get("articles", []):
            title = article.get("title", "No title available")
            doi = article.get("doi", "No DOI available")
            publication_date = article.get("published", "No date available")
            journal = article.get("journal", {}).get("title", "No journal available")
            authors = [author.get("name", "") for author in article.get("authors", [])]

            publication = {
                "doi": doi,
                "journal": journal,
                "publication_date": publication_date,
                "title": title,
                "authors": ", ".join(authors),
            }
            publications.append(publication)

        return publications


def search_multiple_authors(api_key, authors, limit=10):
    """
    Search for publications by multiple authors using the MDPI API.
    :param api_key: MDPI API key (if required).
    :param authors: List of author names to search for.
    :param limit: The number of results to limit for each author (default is 10).
    :return: Dictionary with results for each author.
    """
    mdpi_api = MDPI(api_key)
    all_results = {}

    for author in authors:
        print(f"Searching for publications by {author}...")
        if not author.strip():
            logging.warning("Received empty string for author name, continuing...")
            continue
        try:
            publications = mdpi_api.get_publications_by_author(author, rows=limit)
            all_results[author] = publications
        except Exception as e:
            logging.error(f"Error fetching data for {author}: {e}")

    return all_results


# Example usage
if __name__ == "__main__":
    # Get API key (set it to None if the API does not require authentication)
    api_key = None  # Replace with your MDPI API key if required

    # Input: list of author names (comma-separated input)
    author_names = input("Enter author names (comma-separated): ").split(",")

    # Strip any leading/trailing whitespace
    author_names = [name.strip() for name in author_names]

    # Get results for all authors
    results = search_multiple_authors(api_key, author_names)

    # Output the results in JSON format
    print(json.dumps(results, indent=4))