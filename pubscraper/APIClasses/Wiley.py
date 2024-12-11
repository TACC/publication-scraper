import requests
import urllib.parse
import logging
import xml.etree.ElementTree as ET
import json
from dateutil.parser import parse

from pubscraper.APIClasses.Base import Base
import pubscraper.config as config

LOG_FORMAT = config.LOGGER_FORMAT_STRING
LOG_LEVEL = config.LOGGER_LEVEL
logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger(__name__)


class Wiley(Base):
    def __init__(self):
        """
        Initialize the Wiley Online Library API client.
        """
        self.base_url = config.WILEY_URL

    def get_publications_by_author(self, author_name, rows=10):
        logging.debug(f"requesting {rows} publications from {author_name}")

        if not author_name.strip():
            logging.warning("Received empty string for author name in search query, returning None")
            return None

        # Standardize the author name for query and Construct the full URL
        encoded_author = urllib.parse.quote(author_name)
        query = f"?query=dc.contributor={encoded_author}&maximumRecords={rows}"
        full_url = self.base_url + query

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/xml",
        }

        try:
            response = requests.get(full_url, headers=headers, timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logging.error(f"Wiley API Request error: {e}")
            return []

        return self._parse_response(response.text)

    def _parse_response(self, xml_data):
        """
        Parse the XML response to extract publication details.
        """
        # Log the raw response for debugging
        root = ET.fromstring(xml_data)
        logging.debug(root)

        namespaces = {
            "zs": "http://docs.oasis-open.org/ns/search-ws/sruResponse",
            "dc": "http://purl.org/dc/elements/1.1/",
            "dcterms": "http://purl.org/dc/terms/",
        }

        # Extract publication records
        publications = []
        for record in root.findall(".//zs:recordData", namespaces=namespaces):
            title_elem = record.find(".//dc:title", namespaces=namespaces)
            contributors = record.findall(".//dc:contributor", namespaces=namespaces)
            doi_elememnt = record.find(".//dc:identifier", namespaces=namespaces)
            pub_date_elem = record.find(".//dc:date", namespaces=namespaces)
            part_of_elem = record.find(".//dcterms:isPartOf", namespaces=namespaces)

            title = (
                title_elem.text.strip()
                if title_elem is not None and title_elem.text
                else "No title available"
            )
            authors = [
                contributor.text.strip()
                for contributor in contributors
                if contributor is not None and contributor.text
            ]
            doi = (
                doi_elememnt.text.strip()
                if doi_elememnt is not None and doi_elememnt.text
                else "No DOI available"
            )
            raw_publication_date = (
                pub_date_elem.text.strip()
                if pub_date_elem is not None and pub_date_elem.text
                else "No date available"
            )
            # Standardize the publication date to "YYYY-MM-DD"
            try:
                publication_date = parse(raw_publication_date).strftime("%Y-%m-%d")
            except Exception as e:
                logging.warning(f"Error parsing publication date: {e}")
                publication_date = None
                
            part_of = (
                part_of_elem.text.strip()
                if part_of_elem is not None and part_of_elem.text
                else "No collection available"
            )

            publications.append(
                {
                    "from": "Wiley",
                    "is_part_of": part_of,
                    "publication_date": publication_date,
                    "title": title,
                    "authors": ", ".join(authors),
                    "doi": doi,
                }
            )

        return publications


def search_multiple_authors(authors, limit=10):
    wiley_api = Wiley()
    all_results = {}

    for author in authors:
        logging.debug(f"Searching for publications by {author}...")
        if not author.strip():  # Skip empty author names
            logging.warning("Received empty string for author name, continuing...")
            continue
        try:
            # Get publications for each author
            publications = wiley_api.get_publications_by_author(author, rows=limit)
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
