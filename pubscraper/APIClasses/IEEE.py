import requests
import json
from Base import Base
import config


class IEEEXplore(Base):
    def __init__(self):
        self.base_url = config.IEEE_URL

    def get_publications_by_author(self, author_name, rows=10):
        """
        Retrieve publications from IEEEXplore by author name.
        :param author_name: The name of trhe author to search for
        :param rows: The number of results to return (default is 10)
        :return: a list of dictionaries containing publication details
        """

        # prepare the query parameters
        params = {
            "apikey": api_key,
            "format": "json",
            "max_records": rows,
            "author": author_name.replace(" ", "+"),
        }

        response = requests.get(self.base_url, params=params)

        if response.status_code != 200:
            raise Exception(
                f"Error fetching data from IEEEXplore: {response.status_code}"
            )

        data = response.json()

        publications = []
        # TODO: idk what to put here it would be awesome if IEEE approved my api key
