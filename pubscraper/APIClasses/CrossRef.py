import requests
import json
import logging

format_str = (
    "[%(asctime)s ] %(filename)s:%(funcName)s:%(lineno)s - %(levelname)s: %(message)s"
)
logging.basicConfig(level=logging.DEBUG, format=format_str)


class CrossRef:
    def __init__(self):
        self.base_url = "http://api.crossref.org/works"

    def extract_authors(self, publication_item):
        authors = []
        for author in publication_item["author"]:
            name = author["given"] + " " + author["family"]
            authors.append(name)
            logging.debug(f"added {name} to author list")
        return authors

    def extract_publication_date(self, publication_item):
        logging.debug(json.dumps(publication_item, indent=2))
        try:
            date_list = publication_item["published-print"]["date-parts"]
            return date_list
        except KeyError:  # query does NOT contain publication date
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
            logging.debug(publication_item["title"])
            pub = {
                "journal": publication_item["container-title"],
                "publication_date": self.extract_publication_date(publication_item),
                "title": publication_item["title"][0],
                "authors": self.extract_authors(publication_item),
            }
            publications.append(pub)

        return publications


def search_multiple_authors(authors, rows=10):
    pass


def main() -> None:
    author_names = input("Enter author names(comma-separated): ").split(".")
    author_names = [name.strip() for name in author_names]

    # result = search_multiple_authors(author_names)
    # print(json.dumps(result, indent=2))
    crossref = CrossRef()
    crossref.get_publications_by_author("richard feynman")


if __name__ == "__main__":
    main()
