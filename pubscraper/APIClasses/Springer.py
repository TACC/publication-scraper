import requests
import logging
import json

from pubscraper.APIClasses.Base import Base
import config


class Springer(Base):
    def __init__(self):
        """
        Initialize the Springer (springernature) API client.
        """
        with open("secrets.json") as f:
            secrets = json.load(f)
            api_key = secrets["Springer"]

        self.base_url = config.SPRINGER_URL
        self.api_key = api_key

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

    def get_publications_by_author(self, author_name, rows=10):
        """
        Retrieve publications from Springer by author name, with flexible search options.
        :param author_name: The name of the author to search for (full name, initials, etc.)
        :param rows: The number of results to return (default is 10)
        :return: A list of dictionaries containing publication details
        """
        if not author_name.strip():
            logging.warning(
                "Received empty string for author name in search query, returning None"
            )
            return None

        # Standardize the author name for query
        normalized_name = self._standardize_author_name(author_name)
        params = {
            "q": normalized_name,
            "p": rows,
            "api_key": self.api_key,
        }

        # Error handling when interacting with Springer APIs, Raises HTTP Error for bad responses
        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logging.error(f"Springer API Request error: {e}")
            return []

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
                    "from": "Springer",
                    "journal": publication_name,
                    "content_type": content_type,
                    "publication_date": publication_date,
                    "title": title,
                    "authors": ", ".join(authors),
                    "doi": doi,
                }
                publications.append(publication)

        return publications


def search_multiple_authors(authors, limit=10):
    """
    Search for publications by multiple authors.
    :return: Dictionary with results for each author
    """
    springer_api = Springer()
    all_results = {}

    for author in authors:
        print(f"Searching for publications by {author}...")
        if not author.strip():
            logging.warning("Received empty string for author name, continuing...")
            continue
        try:
            # Get publications for each author, passing the limit (rows) to get_publications_by_author
            publications = springer_api.get_publications_by_author(author, rows=limit)
            all_results[author] = publications if publications else []
        except Exception as e:
            logging.error(f"Error fetching data for {author}: {e}")
            all_results[author] = []

    return all_results


# Example usage:
if __name__ == "__main__":
    # Input: list of author names (comma-separated input)
    author_names = input("Enter author names (comma-separated): ").split(",")

    # Strip any leading/trailing whitespace
    author_names = [name.strip() for name in author_names]

    # Get results for all authors
    results = search_multiple_authors(author_names)

    # Output the results in JSON format
    print(json.dumps(results, indent=4))
