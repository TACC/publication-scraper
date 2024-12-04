import requests
import json
import logging

from pubscraper.APIClasses.Base import Base

# NOTE: we might want to limit results to works published after TACC was founded

"""
Many results from CrossRef are are missing data we're interested in. Currently,
we skip over results with missing data and make another request. If we requested
10 rows, we repeat this process until we have 10 valid publications for each author.
This is a slow process, and we should think about better solutions
"""


class CrossRef(Base):
    def __init__(self):
        self.base_url = "http://api.crossref.org/works"

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
            date_list = publication_item["published-print"]["date-parts"][0]
            date_list = [str(date) for date in date_list]
            logging.debug(f"Successfully extracted date_list: {date_list}")
            date_string = "/".join(date_list)
            return date_string
        except KeyError:  # query does NOT contain publication date
            logging.debug(f"Error fetching published-print from {publication_item} \n")
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

    def get_publications_by_author(self, author_name, rows=10, offset=0):
        """
        Given the name of an author, search CrossRef for works written by
        that author name
        :params author_name: name of author to search
        :params rows: maximum number of publications to return (default is 10)
        :return: a list of publication objects/dics holding UID, journal name,
        publication date, title, and list of authors for each publication
        """

        logging.debug(f"requesting {rows} publications from {author_name}")

        if rows < 0:
            logging.error(f"Rows must be a positive number (received {rows})")
            raise ValueError("Rows must be a positive number")

        if author_name == "":
            logging.warning("received empty string for author name, returning None")
            return None

        params = {
            "query.author": author_name.replace(" ", "+"),
            "rows": rows,
            "select": "author,title,container-title,published-print,DOI",
            "offset": offset,
            "mailto": "jlh7459@my.utexas.edu",
        }

        response = requests.get(self.base_url, params=params)

        if response.status_code != 200:
            logging.error(f"Error fetching data from PubMed: {response.status_code}")
            return None

        data = response.json()
        logging.debug(json.dumps(data, indent=2))

        total_results = data["message"]["total-results"]

        publications = []

        for publication_item in data["message"]["items"]:
            journal = self._extract_journal(publication_item)
            publication_date = self._extract_publication_date(publication_item)
            title = self._extract_title(publication_item)
            authors = self._extract_authors(publication_item)
            doi = publication_item["DOI"]

            pub = {
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

    def _aggregate_publications(self, author: str, rows: int):
        publications = []
        desired_rows = rows
        offset = len(publications)
        logging.debug(
            f"Initial request: requesting {rows} publications from {author} (offset = {offset})"
        )
        while len(publications) < desired_rows:
            total_results, pubs = self.get_publications_by_author(author, rows, offset)
            logging.debug(f"Received {len(pubs)} valid publications for {author}")
            publications += pubs

            if total_results < rows:
                logging.warning(
                    f"Requested {rows} publications from {author}, found {total_results}"
                )
                return publications or None

            offset += rows
            rows -= len(pubs)
            logging.debug(
                f"Requesting {rows} more publications by {author} (offset = {offset})"
            )

        logging.info(
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

        try:
            publications = crossref._aggregate_publications(author, rows)
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
