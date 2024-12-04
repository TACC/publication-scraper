import requests
import json
import time
import logging

from pubscraper.APIClasses.Base import Base
import config


class PubMed(Base):
    def __init__(self):
        self.search_url = config.PUBMED_SEARCH_URL
        self.summary_url = config.PUBMED_SUMMARY_URL

    def _get_UIDs_by_author(self, author_name, rows=10):
        """
        Retrieve a given author's UID publications
        :param author_name: name of author {firstName} {lastName}
        :param rows: number of results to return (default is 10)
        :return: A list of UIDs corresponding to papers written by the author
        """
        # prepare Entrez query

        if rows < 0:
            logging.error(f"Rows must be a postive number (received {rows})")
            raise ValueError("Rows must be a positive number")

        if author_name == "":
            logging.warning("received empty string for author name, returning None")
            return None

        # PubMed searches by {lastName} {firstInitial}{midInitial}
        # searching by {firstName} {lastName} will always yield no results!
        split_name = author_name.split()
        if len(split_name) == 1:
            entrez_author_name = split_name[0] + "[author]"
        else:
            entrez_author_name = split_name[-1] + "+"
            for name in split_name[:-1]:
                entrez_author_name += "{initial}".format(initial=name[0])
            entrez_author_name += "[Author Name]"

        params = {
            "db": "pmc",
            "term": entrez_author_name,
            "retmax": rows,
            "retmode": "JSON",
        }

        # Error handling when interacting with PubMed APIs.
        try:
            response = requests.get(
                self.search_url, params=params, timeout=10
            )  # Send the request to the PubMed API
            response.raise_for_status()  # Raises HTTP Error for bad responses
        except requests.exceptions.RequestException as e:
            logging.error(f"PubMed API Request error: {e}")
            return None

        data = response.json()
        logging.debug(json.dumps(data, indent=2))
        id_list = data["esearchresult"]["idlist"]

        if not id_list:
            logging.warning(
                f"Received no UIDs for author {author_name}, returning None"
            )
            logging.debug(f'passed "{entrez_author_name}" to PubMed API')
            return None

        logging.debug(f"received the following UIDs: {id_list}")
        return id_list

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

    def _get_summary_by_UIDs(self, UIDs):
        """
        Given a list of UIDs, retrieve summary information for each UID
        :params UIDs: a list of UIDs
        :return: a list of publication objects/dicts holding UID, journal
        name, publication date, title, and a list of authors for each publication
        """
        if not UIDs:
            logging.warning("received no UIDs, returning None")
            return None

        # join UIDs list into one 'csv' string
        stringified_UIDs = ",".join(UIDs)
        params = {
            "db": "pmc",
            "id": stringified_UIDs,
            "retmode": "JSON",
        }

        # Error handling when interacting with PubMed APIs.
        try:
            response = requests.get(
                self.search_url, params=params, timeout=10
            )  # Send the request to the PubMed API
            response.raise_for_status()  # Raises HTTP Error for bad responses
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching summaries from PubMed: {e}")
            return None
        response = requests.get(self.summary_url, params=params)

        data = response.json()

        publications = []
        for uid in data["result"]["uids"]:
            summary_object = data["result"][uid]
            author_list = []
            for author_object in summary_object["authors"]:
                author_list.append(author_object["name"])

            pub = {
                "from": "PubMed",
                "journal": summary_object["fulljournalname"],
                "publication_date": summary_object["sortdate"],
                "title": summary_object["title"],
                "authors": ",".join(author_list),
                "doi": self._extract_DOI(summary_object),
            }
            publications.append(pub)

        return publications

    def get_publications_by_author(self, author_name, rows=10):
        """
        Given the name of an author, search PubMed Central for
        works written by that author name
        :params author_name: name of author to search
        :params rows: maximum number of publications to return (default is 10)
        :return: a list of publication objects/dicts holding summary data for each publication
        """
        UIDs = self._get_UIDs_by_author(author_name, rows)
        summary_info = self._get_summary_by_UIDs(UIDs)

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
        logging.info(f"Searching for publications by {author}...")

        if author == "":
            logging.warning("received empty string for author name, continuing...")
            continue

        try:
            publications = pubmed.get_publications_by_author(author, rows)
            all_results[author] = publications
        except Exception as e:
            logging.error(f"Error fetching data for {author}: {e}")
        time.sleep(0.4)  # avoids RESPONSE 429 (rate limit violation)

    return all_results


def main():
    author_names = input("Enter author names (comma-separated): ").split(",")
    author_names = [name.strip() for name in author_names]

    results = search_multiple_authors(author_names)
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
