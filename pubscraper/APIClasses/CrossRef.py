import requests
import json
import logging
from dateutil.parser import parse

from pubscraper.APIClasses.Base import Base
import pubscraper.config as config

logger = logging.getLogger(__name__)

# NOTE: we might want to limit results to works published after TACC was founded

"""
Many results from CrossRef are are missing data we're interested in. Currently,
we skip over results with missing data and make another request. If we requested
10 rows, we repeat this process until we have 10 valid publications for each author.
This is a slow process, and we should think about better solutions
"""


class CrossRef(Base):
    def __init__(self):
        self.base_url = config.CROSSREF_URL

    # TODO: should these extract methods be squished to one method w a switch? ask erik
    def _extract_journal(self, publication_item):
        try:
            journal = publication_item["container-title"][0]
            logging.debug(f"Successfully extracted journal: {journal}")
            return journal
        except KeyError:
            logging.debug(f"Error fetching container-title from {publication_item} \n")
            return None

    def _extract_authors(self, publication_item):
        authors = []
        for author in publication_item["author"]:
            try:
                name = author["given"] + " " + author["family"]
            except KeyError:
                try:
                    name = author["family"]
                except KeyError:
                    logging.debug(f"No author name found in {author} \n")
                    return None
                logging.debug(f"No author name found in {author} \n")
            authors.append(name)
            logging.debug(f"added {name} to author list")
        return (",").join(authors)

    def _extract_publication_date(self, publication_item):
        logging.debug(json.dumps(publication_item, indent=2))
        try:
            # Extract the `date-time` field from the `created` key
            date_time = publication_item.get("created", {}).get("date-time", None)
            if date_time:
                logging.debug(f"Successfully extracted date-time: {date_time}")
                return date_time
            else:
                logging.debug(f"No valid `date-time` found in {publication_item}")
                return None
        except Exception as e:
            logging.error(f"Error extracting `date-time`: {e}")
            return None
        
    def _extract_title(self, publication_item):
        try:
            title = publication_item["title"][0]
            logging.debug(f"Successfuly extracted title: {title}")
            return title
        except KeyError:
            logging.debug(f"Error fetching title from {publication_item} \n")
            return None

    def _is_valid_pub(self, pub: dict[str, str]) -> bool:
        for item in pub:
            if pub[item] is None:
                return False
        return True

    def _aggregate_publications(self, author_name, rows=10, offset=0):
        """
        Given the name of an author, search CrossRef for works written by
        that author name
        :params author_name: name of author to search
        :params rows: maximum number of publications to return (default is 10)
        :return: a list of publication objects/dicts holding UID, journal name,
        publication date, title, and list of authors for each publication
        """

        logging.debug(f"requesting {rows} publications from {author_name}")

        if rows < 0:
            logging.error(f"Rows must be a positive number (received {rows})")
            raise ValueError("Rows must be a positive number")

        if author_name == "":
            logging.warning("received empty string for author name, returning None")
            return 0, None

        params = {
            "query.author": author_name.replace(" ", "+"),
            "rows": rows,
            "offset": offset,
            "mailto": "jlh7459@my.utexas.edu",
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logging.error(f"CrossRef API request error: {e}")
            return []

        data = response.json()
        logging.debug(json.dumps(data, indent=2))

        total_results = data["message"]["total-results"]

        publications = []

        for publication_item in data["message"]["items"]:
            # Extract and standardize the publication date to "YYYY-MM-DD"
            raw_publication_date = self._extract_publication_date(publication_item)
            if raw_publication_date:
                try:
                    publication_date = parse(raw_publication_date).strftime("%Y-%m-%d")
                except Exception as e:
                    logging.warning(f"Error parsing publication date: {e}")
                    publication_date = None
            else:
                publication_date = None

            journal = self._extract_journal(publication_item)
            title = self._extract_title(publication_item)
            authors = self._extract_authors(publication_item)
            doi = publication_item["DOI"]

            pub = {
                "from": "CrossRef",
                "journal": journal,
                "publication_date": publication_date,
                "title": title,
                "authors": authors,
                "doi": doi,
            }

            if self._is_valid_pub(pub):
                publications.append(pub)

        logging.debug(
            f"found {len(publications)} valid publications for author {author_name}"
        )

        return total_results, publications

    def get_publications_by_author(self, author: str, rows: int = 10):
        if rows < 0:
            logging.error(f"Rows must be a positive number (received {rows})")
            raise ValueError("Rows must be a positive number")

        if author == "":
            logging.warning("received empty string for author name, returning None")
            return None

        publications = []
        desired_rows = rows
        offset = len(publications)
        logging.debug(
            f"Initial request: requesting {rows} publications from {author} (offset = {offset})"
        )
        while len(publications) < desired_rows:
            total_results, pubs = self._aggregate_publications(author, rows, offset)
            if pubs is None:
                # an error occured in _aggregate_publications, return None
                return None

            logging.debug(f"Received {len(pubs)} valid publications for {author}")
            publications += pubs

            if total_results < rows:
                logging.warning(
                    f"Requested {rows} publications from {author}, found {total_results}"
                )
                return publications

            offset += rows
            rows -= len(pubs)
            logging.debug(
                f"Requesting {rows} more publications by {author} (offset = {offset})"
            )

        logging.debug(
            f"Retrieved {len(publications)} publications by {author} from CrossRef"
        )
        return publications or None


def search_multiple_authors(authors: list[str], rows: int = 10):
    crossref = CrossRef()
    all_results = {}

    for author in authors:
        logging.debug(f"Searching for publications by {author}...")
        if author == "":
            logging.warning("Received empty string for author name, continuing...")
            continue
        try:
            publications = crossref.get_publications_by_author(author, rows)
            all_results[author] = publications
        except Exception as e:
            logging.error(f"Error fetching data for {author}, {e}")

    return all_results


def main() -> None:
    author_names = input("Enter author names(comma-separated): ").split(",")
    author_names = [name.strip() for name in author_names]

    result = search_multiple_authors(author_names, 10)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
