import requests
import json
import logging
from dateutil.parser import parse

from pubscraper.APIClasses.Base import Base
import pubscraper.config as config

logger = logging.getLogger(__name__)


class PLOS(Base):
    def __init__(self):
        """
        Initialize the arXiv API client.
        """
        self.base_url = config.PLOS_URL

    def get_publications_by_author(self, author_name, rows=10):
        """ "
        Retrieve publications from PLOS by author name.
        :param author_name: The name of the author to search for
        :param rows: The number of results to return (default is 10)
        :return: A list of dictionaries containing publication details
        """
        logging.debug(f"requesting {rows} publications from {author_name}")

        if not author_name.strip():
            logging.warning("Received empty string for author name in search query, returning None")
            return None

        # Prepare the query parameters
        params = {"q": f'author:"{author_name}"', "rows": rows, "wt": "json"}

        # Error handling when interacting with PLOS APIs, Raises HTTP Error for bad responses.
        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logging.error(f"PLOS API Request error: {e}")
            return None

        # Parse the JSON response
        data = response.json()
        logging.debug(json.dumps(data, indent=2))

        # Extract publication records
        publications = []
        for doc in data["response"]["docs"]:
            doi = doc.get("id", "No ID available")
            journal = doc.get("journal", "No journal available")
            article_type = doc.get("article_type", "No article type available")
            
            # Standardize the publication date to "YYYY-MM-DD"
            raw_publication_date = doc.get("publication_date", "No date available")
            try:
                publication_date = parse(raw_publication_date).strftime("%Y-%m-%d")
            except Exception as e:
                logging.warning(f"Error parsing publication date: {e}")
                publication_date = None
            
            title = doc.get("title_display", "No title available")
            authors = doc.get("author_display", [])

            # Create a dictionary with the relevant information
            if all([title, authors, publication_date, journal]):
                publication = {
                    "from": "PLOS",
                    "journal": journal,
                    "content_type": article_type,
                    "publication_date": publication_date,
                    "title": title,
                    "authors": ", ".join(authors),
                    "doi": doi,
                }
                publications.append(publication)

        return publications


# Function to search for multiple authors
def search_multiple_authors(authors, rows=10):
    """
    Search for publications by multiple authors.
    :param authors: The name of the author to search for
    :param rows: The number of results to return (default is 10)
    :return: Dictionary with results for each author
    """
    plos_api = PLOS()
    all_results = {}  # Dictionary to hold results for all authors

    for author in authors:
        logging.debug(f"Searching for publications by {author}...")
        if not author.strip():
            logging.warning("Received empty string for author name, continuing...")
            continue
        try:
            # Get publications for each author
            publications = plos_api.get_publications_by_author(author, rows=rows)
            all_results[author] = publications if publications else []
        except Exception as e:
            logging.error(f"Error fetching data for {author}: {e}")
            all_results[author] = []

    return all_results


# Example usage
if __name__ == "__main__":
    # Input: list of author names (comma-separated input)
    author_names = input("Enter author names (comma-separated): ").split(",")
    author_names = [name.strip() for name in author_names]

    # Get results for all authors
    results = search_multiple_authors(author_names)

    # Output the results in JSON format
    print(json.dumps(results, indent=4))
