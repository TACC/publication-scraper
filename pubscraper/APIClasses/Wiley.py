import requests
import urllib.parse
import logging
import xml.etree.ElementTree as ET
import json

from pubscraper.APIClasses.Base import Base
import pubscraper.config as config


class Wiley(Base):
    def __init__(self):
        """
        Initialize the Wiley Online Library API client.
        """
        self.base_url = config.WILEY_URL

    def _standardize_author_name(self, author_name):
        """
        Standardize author names to handle variations.
        """
        name_parts = author_name.split()

        # Capitalize each part of the name
        name_parts = [part.capitalize() for part in name_parts]

        # If the author has a middle initial, ensure it is followed by a dot
        if len(name_parts) == 3 and len(name_parts[1]) == 1:
            middle_name = name_parts[1]
            # Ensure the middle initial ends with a dot
            if not middle_name.endswith("."):
                middle_name += "."
            return f"{name_parts[0]} {middle_name} {name_parts[2]}"
        elif len(name_parts) == 2:
            return f"{name_parts[0]} {name_parts[1]}"
        else:
            return " ".join(name_parts)

    def get_publications_by_author(self, author_name, rows=10):
        if not author_name.strip():
            logging.warning(
                "Received empty string for author name in search query, returning None"
            )
            return None

        # Standardize the author name for query
        author_name_standardized = self._standardize_author_name(author_name)
        encoded_author = urllib.parse.quote(author_name_standardized)

        # Construct the full URL
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

        # Parse the response
        return self._parse_response(response.text)

    def _parse_response(self, xml_data):
        """
        Parse the XML response to extract publication details.
        """
        root = ET.fromstring(xml_data)
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
            publication_date = (
                pub_date_elem.text.strip()
                if pub_date_elem is not None and pub_date_elem.text
                else "No date available"
            )
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
        print(f"Searching for publications by {author}...")
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
