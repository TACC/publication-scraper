import xml.etree.ElementTree as ET
import requests

from pubscraper.APIClasses.Base import Base
import config


format_str = (
    "[%(asctime)s] %(filename)s:%(funcName)s:%(lineno)d - %(levelname)s: %(message)s"
)
logging.basicConfig(level=logging.DEBUG, format=format_str)


class ArxivAPI(Base):
    def __init__(self):
        """
        Initialize the arXiv API client.
        """
        self.base_url = config.ARXIV_URL

    def standardize_author_name(self, author_name):
        """Standardize the author's name to ensure consistency."""
        name_parts = author_name.split()

        # Capitalize each part of the name
        name_parts = [part.capitalize() for part in name_parts]

        # If the author has a middle initial, ensure it is followed by a dot
        if len(name_parts) == 3 and len(name_parts[1]) == 1:
            # Initial + last name (e.g., Timothy C Moore -> Timothy C. Moore)
            middle_name = name_parts[1] + "."
            return f"{name_parts[0]} {middle_name} {name_parts[2]}"
        elif len(name_parts) == 2:
            # First name + Last name (e.g., Timothy Moore -> Timothy Moore)
            return f"{name_parts[0]} {name_parts[1]}"
        else:
            # Handle other formats (e.g., just first name, last name, etc.)
            return " ".join(name_parts)

    def get_publications_by_author(self, author_name, start=0, max_results=10):
        """Fetch publications from arXiv for a standardized author name."""
        if author_name.strip() == "":
            logging.warning(
                "Received empty string for author name in search query, returning None"
            )
            return None

        # Standardize the author name for query
        author_name_standardized = self.standardize_author_name(author_name)
        params = {
            "search_query": f'au:"{author_name_standardized}"',
            "start": start,
            "max_results": max_results,
        }

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
                self.get_text(author, "{http://www.w3.org/2005/Atom}name")
                for author in entry.findall("{http://www.w3.org/2005/Atom}author")
            ]

            # Check if the exact author name is in the authors list
            if author_name_standardized in authors:
                paper = {
                    "title": self.get_text(entry, "{http://www.w3.org/2005/Atom}title"),
                    "publication_name": self.get_text(
                        entry.find("{http://www.w3.org/2005/Atom}source"),
                        "{http://www.w3.org/2005/Atom}title",
                        "arXiv",
                    ),
                    "publication_date": self.get_text(
                        entry, "{http://www.w3.org/2005/Atom}published"
                    ),
                    "content_type": self.get_text(
                        entry, "{http://www.w3.org/2005/Atom}category", "preprint"
                    ),
                    "doi": self.get_text(
                        entry, "{http://arxiv.org/schemas/atom}doi", ""
                    ),
                    "authors": authors,
                }
                publications.append(paper)

        return publications

    def get_text(self, element, tag, default=""):
        """Helper method to safely get text from XML elements."""
        if element is not None:
            found_element = element.find(tag)
            if found_element is not None:
                return found_element.text
        return default


def search_multiple_authors(authors, max_results=10):
    arxiv_api = ArxivAPI()
    all_results = {}

    for author in authors:
        print(f"Searching for publications by {author}...")
        if not author.strip():  # Skip empty author names
            continue
        try:
            # Get publications for each author
            publications = arxiv_api.get_publications_by_author(
                author, max_results=max_results
            )
            all_results[author] = publications
        except Exception as e:
            logging.error(f"Error fetching data for {author}: {e}")
            all_results[author] = []

    return all_results


if __name__ == "__main__":
    # Input: list of author names (comma-separated input)
    author_names = input("Enter author names (comma-separated): ").split(",")

    # Strip any leading/trailing whitespace
    author_names = [name.strip() for name in author_names]

    # Get results for all authors
    results = search_multiple_authors(author_names)

    # Output the results in JSON format
    print(json.dumps(results, indent=4))
