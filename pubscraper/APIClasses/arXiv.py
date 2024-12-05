import xml.etree.ElementTree as ET
import json
import logging
import requests

from pubscraper.APIClasses.Base import Base
import config


class ArXiv(Base):
    def __init__(self):
        """
        Initialize the arXiv API client.
        """
        self.base_url = config.ARXIV_URL

    def _standardize_author_name(self, author_name):
        """Standardize the author's name to ensure consistency."""
        name_parts = author_name.split()

        # Capitalize each part of the name
        name_parts = [part.capitalize() for part in name_parts]

        # If the author has a middle initial, ensure it is followed by a dot
        if len(name_parts) == 3 and len(name_parts[1]) == 1:
            middle_name = name_parts[1]
            if not middle_name.endswith("."):
                middle_name += "."
            return f"{name_parts[0]} {middle_name} {name_parts[2]}"
        elif len(name_parts) == 2:
            return f"{name_parts[0]} {name_parts[1]}"
        else:
            return " ".join(name_parts)

    def get_publications_by_author(self, author_name, start=0, max_results=10):
        """"
        Retrieve publications from PLOS by author name.
        :param author_name: The name of the author to search for
        :param rows: The number of results to return (default is 10)
        :return: A list of dictionaries containing publication details
        """
        if not author_name.strip():
            logging.warning(
                "Received empty string for author name in search query, returning None"
            )
            return None

        # Standardize the author name for query
        author_name_standardized = self._standardize_author_name(author_name)
        params = {
            "search_query": f'au:"{author_name_standardized}"',
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

        root = ET.fromstring(response.text)
        
        publications = []

        for entry in root.findall("{http://www.w3.org/2005/Atom}entry"):
            authors = [
                self._get_text(author, "{http://www.w3.org/2005/Atom}name")
                for author in entry.findall("{http://www.w3.org/2005/Atom}author")
            ]

            # Check if the exact author name is in the authors list
            if author_name_standardized in authors:
                paper = {
                    "from": "ArXiv",
                    "title": self._get_text(
                        entry, "{http://www.w3.org/2005/Atom}title"
                    ),
                    "publication_name": self._get_text(
                        entry.find("{http://www.w3.org/2005/Atom}source"),
                        "{http://www.w3.org/2005/Atom}title",
                        "arXiv",
                    ),
                    "publication_date": self._get_text(
                        entry, "{http://www.w3.org/2005/Atom}published"
                    ),
                    "content_type": self._get_text(
                        entry, "{http://www.w3.org/2005/Atom}category", "preprint"
                    ),
                    "authors": authors,
                    "doi": self._get_text(
                        entry, "{http://arxiv.org/schemas/atom}doi", ""
                    ),
                }
                publications.append(paper)

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
        print(f"Searching for publications by {author}...")
        if not author.strip():
            logging.warning("Received empty string for author name, continuing...")
            continue
        try:
            # Get publications for each author, passing the limit (rows) to get_publications_by_author
            publications = arxiv_api.get_publications_by_author(
                author, max_results=max_results
            )
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
