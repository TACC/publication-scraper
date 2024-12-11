import requests
import json
import logging
import os

from dotenv import load_dotenv
from dateutil.parser import parse

from pubscraper.APIClasses.Base import Base
import pubscraper.config as config

LOG_FORMAT = config.LOGGER_FORMAT_STRING
LOG_LEVEL = config.LOGGER_LEVEL
logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger(__name__)

class Elsevier(Base):
    def __init__(self):
        """
        Initialize the Elsevier API client.
        """
        load_dotenv()
        self.base_url = config.ELSEVIER_URL
        self.api_key = os.getenv("ELSEVIER")

    def get_publications_by_author(self, author_name, rows=10):
        """
        Retrieve publications from Elsevier by author name.
        :param author_name: The name of the author to search for
        :param rows: The number of results to return (default is 10)
        :return: A list of dictionaries containing publication details
        """
        logging.debug(f"requesting {rows} publications from {author_name}")

        if not author_name.strip():
            logging.warning("Received empty string for author name, skipping search.")
            return None

        # Prepare the query parameters
        params = {
            "query": f"AUTHOR-NAME({author_name})",
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
        logging.debug(json.dumps(data, indent=2))

        # Check if total results are greater than 0, will still get 200 even if theres publication
        total_results = int(data.get("search-results", {}).get("opensearch:totalResults", 0))
        if total_results == 0:
            logging.debug(f"No publications found for {author_name}.")
            return []

        # Extract publication records
        publications = []
        for record in data.get("search-results", {}).get("entry", []):
            # Standardize the publication date to "YYYY-MM-DD"
            raw_publication_date = record.get("prism:coverDate", "No date available")
            try:
                publication_date = parse(raw_publication_date).strftime("%Y-%m-%d")
            except Exception as e:
                logging.warning(f"Error parsing publication date: {e}")
                publication_date = None

            title = record.get("dc:title", "No title available")
            publication_name = record.get("prism:publicationName", "No journal available")
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
                "from": "Elsevier",
                "journal": publication_name,
                "content_type": content_type,
                "publication_date": publication_date,
                "title": title,
                "authors": ", ".join(authors),
                "doi": doi,
            }
            publications.append(publication)
        logging.debug(f"found {len(publications)} valid publications for author {author_name}")

        return publications


def search_multiple_authors(authors, limit=10):
    """
    Search for publications by multiple authors.
    :param authors: List of author names to search for
    :param limit: The number of results to return (default is 10)
    :return: Dictionary with results for each author
    """
    elsevier_api = Elsevier()
    all_results = {}  # Dictionary to hold results for all authors

    for author in authors:
        logging.debug(f"Searching for publications by {author}...")
        if not author.strip():
            logging.warning("Received empty string for author name, continuing...")
            continue
        try:
            # Get publications for each author
            publications = elsevier_api.get_publications_by_author(author, rows=limit)
            all_results[author] = publications if publications else []
        except Exception as e:
            logging.error(f"Error fetching data for {author}: {e}")
            all_results[author] = []

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
