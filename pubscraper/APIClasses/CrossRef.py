import requests
import json
import logging

format_str = (
    "[%(asctime)s ] %(filename)s:%(funcName)s:%(lineno)s - %(levelname)s: %(message)s"
)
logging.basicConfig(level=logging.WARNING, format=format_str)


class CrossRef:
    def __init__(self):
        self.base_url = "http://api.crossref.org/works"

    # TODO: should these extract methods be squished to one method w a switch? ask erik
    def extract_journal(self, publication_item):
        try:
            journal = publication_item["container-title"][0]
            logging.info(f"Successfully extracted journal: {journal}")
            return journal
        except KeyError:
            logging.error(f"Error fetching container-title from {publication_item}")
            return None

    def extract_authors(self, publication_item):
        authors = []
        for author in publication_item["author"]:
            try:
                name = author["given"] + " " + author["family"]
            except KeyError:
                name = author["family"]
            except Exception:
                logging.error(f"No author name found in {author}")
                return None
            authors.append(name)
            logging.info(f"added {name} to author list")
        return authors

    def extract_publication_date(self, publication_item):
        logging.debug(json.dumps(publication_item, indent=2))
        try:
            date_list = publication_item["published-print"]["date-parts"][0]
            date_list = [str(date) for date in date_list]
            logging.info(f"Successfully extracted date_list: {date_list}")
            date_string = "-".join(date_list)
            return date_string
        except KeyError:  # query does NOT contain publication date
            logging.error(f"Error fetching published-print fron {publication_item}")
            return None

    def extract_title(self, publication_item):
        try:
            title = publication_item["title"][0]
            logging.info(f"Successfuly extracted title: {title}")
            return title
        except KeyError:
            logging.error(f"Error fetching title from {publication_item}")
            return None

    def get_publications_by_author(self, author_name, rows=10):
        """
        Given the name of an author, search CrossRef for works written by
        that author name
        :params author_name: name of author to search
        :params rows: maximum number of publications to return (default is 10)
        :return: a list of publication objects/dics holding UID, journal name,
        publication date, title, and list of authors for each publication
        """

        if rows < 0:
            logging.error(f"Rows must be a positive number (received {rows})")
            raise ValueError("Rows must be a positive number")

        if author_name == "":
            logging.warning("received empty string for author name, returning None")

        params = {
            "query.author": author_name.replace(" ", "+"),
            "rows": "10",
            "select": "author,title,container-title,published-print",
        }

        response = requests.get(self.base_url, params=params)

        if response.status_code != 200:
            logging.error(f"Error fetching data from PubMed: {response.status_code}")
            return None

        data = response.json()
        logging.debug(json.dumps(data, indent=2))

        publications = []

        for publication_item in data["message"]["items"]:
            journal = self.extract_journal(publication_item)
            publication_date = self.extract_publication_date(publication_item)
            title = self.extract_title(publication_item)
            authors = self.extract_authors(publication_item)

            pub = {
                "journal": journal,
                "publication_date": publication_date,
                "title": title,
                "authors": authors,
            }
            publications.append(pub)

        return publications


def search_multiple_authors(authors: list[str], rows: int = 10):
    crossref = CrossRef()
    all_results = {}

    for author in authors:
        logging.info(f"Searching for publications by {author}...")

        if author == "":
            logging.warning("Received empty string for author name, continuing...")

        try:
            publications = crossref.get_publications_by_author(author, rows)
            all_results[author] = publications
        except Exception as e:
            logging.error(f"Error fetching data for {author}, {e}")

    return all_results


def main() -> None:
    author_names = input("Enter author names(comma-separated): ").split(",")
    author_names = [name.strip() for name in author_names]

    result = search_multiple_authors(author_names, 1)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
