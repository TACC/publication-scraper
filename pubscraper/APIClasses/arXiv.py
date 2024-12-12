import xml.etree.ElementTree as ET
import json
import logging
import requests
from dateutil.parser import parse

from pubscraper.APIClasses.Base import Base
import pubscraper.config as config

logger = logging.getLogger(__name__)

class ArXiv(Base):
    def __init__(self):
        """
        Initialize the arXiv API client.
        """
        self.base_url = config.ARXIV_URL

    def get_publications_by_author(self, author_name, start=0, max_results=10):
        """ "
        Retrieve publications from PLOS by author name.
        :param author_name: The name of the author to search for
        :param rows: The number of results to return (default is 10)
        :return: A list of dictionaries containing publication details
        """
        logging.debug(f"requesting {max_results} publications from {author_name}")

        if not author_name.strip():
            logging.warning("Received empty string for author name in search query, returning None")
            return None

        params = {
            "search_query": f'au:"{author_name}"',
            "start": start,
            "max_results": max_results,
        }

        # Error handling when interacting with arXiv APIs, Raises HTTP Error for bad responses
        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logging.error(f"arXiv API Request error: {e}")
            return []

        # Log the raw response for debugging
        root = ET.fromstring(response.text)
        logging.debug(root)

        publications = []

        for entry in root.findall("{http://www.w3.org/2005/Atom}entry"):
            authors = [self._get_text(author, "{http://www.w3.org/2005/Atom}name") for author in entry.findall("{http://www.w3.org/2005/Atom}author")]

            # Check if the exact author name is in the authors list
            if author_name in authors:
                raw_publication_date = self._get_text(entry, "{http://www.w3.org/2005/Atom}published")  # Extract the raw publication date
                # Standardize the publication date to "YYYY-MM-DD"
                try:
                    publication_date = parse(raw_publication_date).strftime("%Y-%m-%d")
                except Exception as e:
                    logging.warning(f"Error parsing publication date: {e}")
                    publication_date = None 

                # Extract journal_ref (if it exists)
                journal_ref = self._get_text(entry.find("{http://arxiv.org/schemas/atom}journal_ref"), "")

                paper = {
                    "from": "ArXiv",
                    "title": self._get_text(entry, "{http://www.w3.org/2005/Atom}title"),
                    "journal": journal_ref,
                    "publication_date": publication_date,
                    "content_type": self._get_text(entry, "{http://www.w3.org/2005/Atom}category", "preprint"),
                    "authors": authors,
                    "doi": self._get_text(entry, "{http://arxiv.org/schemas/atom}doi", "")
                }
                publications.append(paper)
        logging.debug(f"Retrieved {len(publications)} publications by {author_name} from CrossRef" )
        return publications

    def _get_text(self, element, tag, default=""):
        """Helper method to safely get text from XML elements."""
        if element is not None:
            found_element = element.find(tag)
            if found_element is not None:
                return found_element.text
        return default


def search_multiple_authors(authors, max_results=10):
    """
    Search for publications by multiple authors.
    :param authors: List of author names to search for
    :return: Dictionary with results for each author
    """
    arxiv_api = ArXiv()
    all_results = {}  # Dictionary to hold results for all authors

    for author in authors:
        logging.debug(f"Searching for publications by {author}...")
        if not author.strip():
            logging.warning("Received empty string for author name, continuing...")
            continue
        try:
            # Get publications for each author, passing the limit (rows) to get_publications_by_author
            publications = arxiv_api.get_publications_by_author(author, max_results=max_results)
            all_results[author] = publications if publications else []
        except Exception as e:
            logging.error(f"Error fetching data for {author}: {e}")
            all_results[author] = []

    return all_results


if __name__ == "__main__":
    # Input: list of author names (comma-separated input)
    author_names = input("Enter author names (comma-separated): ").split(",")
    author_names = [name.strip() for name in author_names]

    # Get results for all authors
    results = search_multiple_authors(author_names)

    # Output the results in JSON format
    print(json.dumps(results, indent=4))
