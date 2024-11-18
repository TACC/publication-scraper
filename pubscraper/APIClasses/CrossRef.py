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
        }

        response = requests.get(self.base_url, params=params)

        if response.status_code != 200:
            logging.error(f"Error fetching data from PubMed: {response.status_code}")
            return None

        data = response.json()
        logging.debug(json.dumps(data, indent=2))
