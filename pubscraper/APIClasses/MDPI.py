# import requests
# import logging
# import json

# from pubscraper.APIClasses.Base import Base
# import pubscraper.config as config


# class MDPI(Base):
#     def __init__(self):
#         """api
#         Initialize the MDPI API client.
#         """
#         self.base_url = config.MDPI_URL

#     def _standardize_author_name(self, author_name):
#         """
#         Standardize author names to handle variations like "T C Moore", "Timothy C Moore", and "Timothy C. Moore".
#         :param author_name: The name to standardize
#         :return: Standardized author name in the format "Timothy C. Moore"
#         """
#         name_parts = author_name.split()

#         # Capitalize each part of the name
#         name_parts = [part.capitalize() for part in name_parts]

#         # If the author has a middle initial, ensure it is followed by a dot
#         if len(name_parts) == 3 and len(name_parts[1]) == 1:
#             # Make sure the middle initial is followed by a dot
#             middle_name = name_parts[1] + "."
#             return f"{name_parts[0]} {middle_name} {name_parts[2]}"
#         elif len(name_parts) == 2:  # No middle name, just first and last name
#             return f"{name_parts[0]} {name_parts[1]}"
#         else:
#             # Handle other cases (like middle name fully spelled out)
#             return " ".join(name_parts)

#     def get_publications_by_author(self, author_name, rows=10):
#         """
#         Retrieve publications from MDPI by author name.
#         :param author_name: The name of the author to search for.
#         :param rows: The number of results to return (default is 10).
#         :return: A list of dictionaries containing publication details.
#         """
#         if not author_name.strip():
#             logging.warning(
#                 "Received empty string for author name in search query, returning None"
#             )
#             return None

#         # Normalize the author name before querying
#         normalized_name = self._standardize_author_name(author_name)

#         # Prepare the query parameters
#         params = {
#             'query.author': author_name,
#             'filter': f'publisher:{normalized_name}',
#             'rows': rows,
#             'mailto':"ma57489@my.utexas.edu"
#             # 'mailto': self.headers.get('User-Agent', '')
#         }

#         # Error handling when interacting with MDPI APIs, Raises HTTP Error for bad responses.
#         try:
#             response = requests.get(self.base_url, params=params, timeout=10)
#             response.raise_for_status()
#         except requests.exceptions.RequestException as e:
#             logging.error(f"MDPI API Request error: {e}")
#             return None

#         # Parse the JSON response
#         data = response.json()

#         # Extract publication records
#         publications = []
#         for article in data.get("articles", []):
#             title = article.get("title", "No title available")
#             doi = article.get("doi", "No DOI available")
#             publication_date = article.get("published", "No date available")
#             journal = article.get("journal", {}).get("title", "No journal available")
#             authors = [author.get("name", "") for author in article.get("authors", [])]

#             publication = {
#                 "from": "MDPI",
#                 "journal": journal,
#                 "publication_date": publication_date,
#                 "title": title,
#                 "authors": ", ".join(authors),
#                 "doi": doi,
#             }
#             publications.append(publication)

#         return publications


# def search_multiple_authors(api_key, authors, limit=10):
#     """
#     Search for publications by multiple authors using the MDPI API.
#     :param api_key: MDPI API key (if required).
#     :param authors: List of author names to search for.
#     :param limit: The number of results to limit for each author (default is 10).
#     :return: Dictionary with results for each author.
#     """
#     mdpi_api = MDPI(api_key)
#     all_results = {}

#     for author in authors:
#         print(f"Searching for publications by {author}...")
#         if not author.strip():
#             logging.warning("Received empty string for author name, continuing...")
#             continue
#         try:
#             publications = mdpi_api.get_publications_by_author(author, rows=limit)
#             all_results[author] = publications
#         except Exception as e:
#             logging.error(f"Error fetching data for {author}: {e}")

#     return all_results


# # Example usage
# if __name__ == "__main__":
#     # Input: list of author names (comma-separated input)
#     author_names = input("Enter author names (comma-separated): ").split(",")

#     # Strip any leading/trailing whitespace
#     author_names = [name.strip() for name in author_names]

#     # Get results for all authors
#     results = search_multiple_authors(author_names)

#     # Output the results in JSON format
#     print(json.dumps(results, indent=4))



import requests
import json
import logging

# Configure logging
format_str = "[%(asctime)s] %(filename)s:%(funcName)s:%(lineno)d - %(levelname)s: %(message)s"
logging.basicConfig(level=logging.DEBUG, format=format_str)

class MDPI:
    def __init__(self):
        """
        Initialize the Crossref API client.
        """
        self.base_url = "https://api.crossref.org/works"  # Crossref API base URL

    def get_publications_by_author(self, author_name, rows=10, offset=0):
        """
        Retrieve publications from Crossref by author name.
        
        :param author_name: The name of the author to search for
        :param rows: The number of results to return (default is 10)
        :return: A list of dictionaries containing publication details
        """
        params = {
            "query.author": author_name.replace(" ", "+"),
            "rows": rows,
            # "select": "author,title,container-title,published-print,DOI",
            "offset": offset,
            "mailto": "jlh7459@my.utexas.edu",
        }

        # Send request to Crossref API
        response = requests.get(self.base_url, params=params)
        
        if response.status_code != 200:
            logging.error(f"Error fetching data: {response.status_code}")
            return []

        data = response.json()

        publications = []
        for item in data.get('message', {}).get('items', []):
            publication = {
                "title": item.get("title", ["No Title"])[0],
                "author": item.get("author", [{"given": "Unknown", "family": "Unknown"}])[0],
                "journal": item.get("container-title", ["No Journal"])[0],
                "doi": item.get("DOI", "No DOI"),
                "published": item.get("published", {}).get("date-time", "Unknown Date")
            }
            publications.append(publication)

        return publications

# Function to search for multiple authors
def search_multiple_authors(authors, rows=10):
    """
    Search for publications by multiple authors.
    :param authors: List of author names to search for
    :param rows: The number of results to return (default is 10)
    :return: Dictionary with results for each author
    """
    mdpi = MDPI()
    all_results = {}  # Dictionary to hold results for all authors

    for author in authors:
        print(f"Searching for publications by {author}...")
        if not author.strip():
            logging.warning("Received empty string for author name, continuing...")
            continue
        try:
            # Get publications for each author
            publications = mdpi.get_publications_by_author(author, rows=rows)
            all_results[author] = publications if publications else []
        except Exception as e:
            logging.error(f"Error fetching data for {author}: {e}")
            all_results[author] = []

    return all_results

# Example usage
if __name__ == "__main__":
    # Input: list of author names (comma-separated input)
    author_names = input("Enter author names (comma-separated): ").split(",")
    author_names = [name.strip() for name in author_names]

    # Get results for all authors
    results = search_multiple_authors(author_names)

    # Output the results in JSON format
    print(json.dumps(results, indent=4))
