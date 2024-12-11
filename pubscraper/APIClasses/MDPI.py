import requests
import json
import logging
from dateutil.parser import parse

from pubscraper.APIClasses.Base import Base
import pubscraper.config as config

LOG_FORMAT = config.LOGGER_FORMAT_STRING
LOG_LEVEL = config.LOGGER_LEVEL
logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger(__name__)


class MDPI(Base):
    def __init__(self):
        """
        Initialize the MDPI Library API client.
        """
        self.base_url = config.MDPI_URL

    def get_publications_by_author(self, author_name, rows=10, offset=0):
        """
        Retrieve publications from MDPI by author name.
        :param author_name: The name of the author to search for.
        :param rows: The number of results to return (default is 10).
        :param offset: Offset for paginated results (default is 0).
        :return: A list of dictionaries containing publication details.
        """
        params = {
            "query.author": author_name.replace(" ", "+"),
            "rows": rows,
            "offset": offset,
            "mailto": "ma57489@my.utexas.edu",
        }

        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logging.error(f"MDPI API request error: {e}")
            return []

        # Parse the JSON response
        data = response.json()

        publications = []

        # Extract publication records
        for item in data.get("message", {}).get("items", []):
            authors = [f"{author.get('given', '')} {author.get('family', '')}"for author in item.get("author", [])]
            
            # Standardize the publication date to "YYYY-MM-DD"
            raw_date_time = item.get("created", {}).get("date-time", None)
            if raw_date_time:
                try:
                    # Parse the date-time and extract the date in "YYYY-MM-DD" format
                    publication_date = parse(raw_date_time).strftime("%Y-%m-%d")
                except Exception as e:
                    logging.info(f"Error parsing date-time: {e}")
                    return None
            else:
                logging.info("No valid `date-time` available.")
                return None

            # Create a dictionary with the relevant information
            publication = {
                "from": "MDPI",
                "journal": item.get("container-title", ["No Journal"])[0],
                "content_type": item.get("type", "Unknown"),
                "publication_date": publication_date,
                "title": item.get("title", ["No Title"])[0],
                "authors": ", ".join(authors) if authors else "Unknown",
                "doi": item.get("DOI", "No DOI"),
            }
            publications.append(publication)

        return publications

def search_multiple_authors(authors, rows=10):
    """
    Search for publications by multiple authors.
    :param authors: List of author names to search for.
    :param rows: The number of results to return (default is 10).
    :return: Dictionary with results for each author.
    """
    mdpi = MDPI()
    all_results = {} 

    for author in authors:
        print(f"Searching for publications by {author}...")
        if not author.strip():
            logging.warning("Received empty string for author name, continuing...")
            continue
        try:
            # Get publications for each author
            publications = mdpi.get_publications_by_author(author, rows=rows)
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
