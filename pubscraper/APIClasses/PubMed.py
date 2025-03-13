import requests
import json
import time
import logging
from dateutil.parser import parse
from ratelimit import limits, sleep_and_retry
import os

from pubscraper.APIClasses.Base import Base
import pubscraper.config as config

logger = logging.getLogger(__name__)

class PubMed(Base):
    def __init__(self):
        self.search_url = config.PUBMED_SEARCH_URL
        self.summary_url = config.PUBMED_SUMMARY_URL
        self.fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"  # Add efetch URL
        # Add rate limit info to debug output
        logging.debug(f"PubMed API rate limit: 2 requests per second (API limit is 3/second)")

    @sleep_and_retry
    @limits(calls=2, period=1)  # Use 2 requests per second for safety (PubMed API limit is 3 per second)
    def _make_request(self, url, params):
        try:
            response = requests.get(url, params=params, timeout=10)
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching data from {url}: {e}")
            raise
        response.raise_for_status()
        return response

    def _get_UIDs_by_author(self, author_name, rows=10):
        """
        Retrieve a given author's UID publications
        :param author_name: name of author in format "Last First [Middle]"
        :param rows: number of results to return (default is 10)
        :return: A list of UIDs corresponding to papers written by the author
        """
        if not author_name or author_name == "":
            logging.debug("Skipping empty author name")
            return None

        # Split the name and format for PubMed's search
        split_name = author_name.split()
        if len(split_name) < 2:
            logging.warning(f"Invalid author name format: {author_name}")
            return None
        
        # Try different search formats
        # Format 1: Last+First+Middle[Full Author Name]
        name_search1 = f"{split_name[0]}+{'+'.join(split_name[1:])}[Full Author Name]"
        # Format 2: Last+First[Author]
        name_search2 = f"{split_name[0]}+{split_name[1]}[Author]"
        
        logging.debug(f"Trying search formats:")
        logging.debug(f"1: {name_search1}")
        logging.debug(f"2: {name_search2}")

        for search_term in [name_search1, name_search2]:
            params = {
                "db": "pubmed",  # Try pubmed instead of pmc
                "term": search_term,
                "retmax": rows,
                "retmode": "JSON",
            }

            try:
                # Log the full URL being called
                query_url = f"{self.search_url}?{'&'.join(f'{k}={v}' for k, v in params.items())}"
                logging.debug(f"Making request to: {query_url}")
                
                response = self._make_request(self.search_url, params=params)
                data = response.json()
                
                # Log the response
                logging.debug(f"Response: {json.dumps(data, indent=2)}")
                
                if "esearchresult" in data and "idlist" in data["esearchresult"]:
                    id_list = data["esearchresult"]["idlist"]
                    if id_list:
                        logging.info(f"Found {len(id_list)} publications for {author_name}")
                        return id_list
                
            except Exception as e:
                logging.error(f"PubMed API Request error: {e}")
                continue

        logging.info(f"No publications found for author: {author_name}")
        return None

    def _extract_DOI(self, summary_object) -> str:
        """
        Given a JSON object of a publication, extract and return the DOI
        :params summary_object: JSON result from PubMed eSummary
        :return: DOI of the article as a string
        """
        articleids = summary_object.get("articleids", [])
        for id in articleids:
            if id["idtype"] == "doi":
                return id["value"]

        return ""

    def _get_detailed_info(self, UIDs):
        """
        Get detailed publication information including affiliations using efetch
        :params UIDs: list of UIDs
        :return: detailed publication data
        """
        if not UIDs:
            return None

        params = {
            "db": "pubmed",
            "id": ",".join(UIDs),
            "retmode": "xml"  # efetch works better with XML for detailed data
        }

        try:
            response = self._make_request(self.fetch_url, params=params)
            # We'll need to parse XML response to get affiliations
            from xml.etree import ElementTree as ET
            root = ET.fromstring(response.text)
            
            pub_details = {}
            for article in root.findall(".//PubmedArticle"):
                pmid = article.find(".//PMID").text
                affiliations = []
                
                # Get all author affiliations
                author_list = article.findall(".//Author")
                for author in author_list:
                    author_name_elements = []
                    last_name = author.find("LastName")
                    fore_name = author.find("ForeName")
                    if last_name is not None:
                        author_name_elements.append(last_name.text)
                    if fore_name is not None:
                        author_name_elements.append(fore_name.text)
                    author_name = " ".join(author_name_elements)

                    # Get affiliations for this author
                    aff_list = author.findall(".//AffiliationInfo/Affiliation")
                    author_affiliations = [aff.text for aff in aff_list if aff.text]
                    
                    if author_affiliations:
                        affiliations.append({
                            "author": author_name,
                            "affiliations": author_affiliations
                        })
                
                pub_details[pmid] = affiliations
                
            return pub_details
        except Exception as e:
            logging.error(f"Error fetching detailed info: {e}")
            return None

    def _check_ut_affiliation(self, affiliations):
        """
        Check if any affiliation contains UT system keywords
        :param affiliations: List of affiliation dictionaries
        :return: Boolean indicating if UT system affiliation is present
        """
        if not affiliations:
            return False
        
        for author_info in affiliations:
            for affiliation in author_info.get('affiliations', []):
                if not affiliation:
                    continue
                if 'university of texas' in affiliation.lower():
                    logging.debug(f"Found UT affiliation: {affiliation}")
                    return True
        
        return False

    def _get_summary_by_UIDs(self, UIDs):
        """
        Given a list of UIDs, retrieve summary information for each UID
        :params UIDs: a list of UIDs
        :return: a list of publication objects/dicts holding summary data
        """
        if not UIDs:
            logging.debug("No UIDs provided to fetch summaries")
            return None

        # Get basic summary data
        params = {
            "db": "pubmed",
            "id": ",".join(UIDs),
            "retmode": "JSON"
        }

        try:
            # Get both summary and detailed (affiliation) data
            response = self._make_request(self.summary_url, params=params)
            data = response.json()
            
            # Get detailed info including affiliations
            detailed_info = self._get_detailed_info(UIDs)
            
            publications = []
            if "result" in data:
                result = data["result"]
                if isinstance(result, dict) and "uids" in result:
                    for uid in result["uids"]:
                        try:
                            summary_object = result[uid]
                            
                            # Skip if no detailed info available
                            if not detailed_info or uid not in detailed_info:
                                logging.debug(f"No detailed info for publication {uid}")
                                continue
                            
                            # Check for UT system affiliation
                            affiliations = detailed_info.get(uid, [])
                            if not self._check_ut_affiliation(affiliations):
                                logging.debug(f"Publication {uid} has no UT system affiliation")
                                continue

                            # Get basic publication info
                            author_list = []
                            if "authors" in summary_object:
                                for author in summary_object.get("authors", []):
                                    if isinstance(author, dict) and "name" in author:
                                        author_list.append(author["name"])

                            # Get publication date
                            publication_date = None
                            if "sortdate" in summary_object:
                                try:
                                    publication_date = parse(summary_object["sortdate"]).strftime("%Y-%m-%d")
                                except Exception as e:
                                    logging.warning(f"Error parsing date: {e}")

                            pub = {
                                "from": "PubMed",
                                "journal": summary_object.get("fulljournalname", ""),
                                "publication_date": publication_date,
                                "title": summary_object.get("title", ""),
                                "authors": ",".join(author_list) if author_list else "",
                                "affiliations": affiliations,
                                "doi": self._extract_DOI(summary_object),
                            }
                            publications.append(pub)
                        except Exception as e:
                            logging.warning(f"Error processing publication {uid}: {e}")
                            continue

            if publications:
                logging.info(f"Successfully processed {len(publications)} publications with UT system affiliations")
                return publications
            else:
                logging.warning("No publications with UT system affiliations found")
                return None

        except Exception as e:
            logging.error(f"Error fetching data from PubMed: {e}")
            return None

    def get_publications_by_author(self, author_name, rows=10):
        """
        Given the name of an author, search PubMed Central for
        works written by that author name
        :params author_name: name of author to search
        :params rows: maximum number of publications to return (default is 10)
        :return: a list of publication objects/dicts holding summary data for each publication
        """
        logging.debug(f"Fetching publications for author: {author_name}")
        UIDs = self._get_UIDs_by_author(author_name, rows)
        if not UIDs:
            logging.info(f"No publications found for {author_name}")
            return None
        
        summary_info = self._get_summary_by_UIDs(UIDs)
        if summary_info:
            logging.debug(f"Successfully retrieved {len(summary_info)} publication summaries")
        return summary_info


def search_multiple_authors(authors, rows=10):
    """
    Search PubMed Central for works written by multiple authors
    :params authors: list of author names
    :params rows: maximum number of publications to return per author (default is 10)
    :return: a dict {author_name: {summary_info}} for each author
    """
    pubmed = PubMed()
    all_results = {}

    for author in authors:
        logging.debug(f"Searching for publications by {author}...")
        if not author or author == "None None":  # Skip empty or None None authors
            logging.warning(f"Skipping invalid author name: {author}")
            continue
        try:
            publications = pubmed.get_publications_by_author(author, rows)
            if publications:  # Only add authors with valid publications
                all_results[author] = publications
        except Exception as e:
            logging.error(f"Error fetching data for {author}: {e}")
        time.sleep(0.4)  # avoids RESPONSE 429 (rate limit violation)

    return all_results


def main():
    author_names = input("Enter author names (comma-separated): ").split(",")
    author_names = [name.strip() for name in author_names]

    # Add debug information
    try:
        import pubscraper.config as config
        print(f"Current WS_NAME in config: {config.WS_NAME}")
        
        # If you're using openpyxl, add this:
        from openpyxl import load_workbook
        wb = load_workbook('example_UTRC_report_October-2024.xlsx')
        print(f"Available worksheets: {wb.sheetnames}")
        
        results = search_multiple_authors(author_names)
        print(json.dumps(results, indent=2))
    except Exception as e:
        print(f"Error occurred: {type(e).__name__}: {str(e)}")
        print(f"Current working directory: {os.getcwd()}")


if __name__ == "__main__":
    main()
