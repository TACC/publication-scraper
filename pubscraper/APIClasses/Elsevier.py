import requests
import json
import re
import logging

# Set up basic logging
format_str = "[%(asctime)s] %(filename)s:%(funcName)s:%(lineno)d - %(levelname)s: %(message)s"
logging.basicConfig(level=logging.DEBUG, format=format_str)

class Elsevier:
    def __init__(self, api_key):
        """
        Initialize the Elsevier API client.
        :param api_key: Your Elsevier API key
        """
        self.base_url = "https://api.elsevier.com/content/search/scopus"
        self.api_key = api_key

    def normalize_author_name(self, author_name):
        """
        Normalize author name to the most consistent format for querying the Elsevier API.
        :param author_name: Author's name (either in "First Last" or "Last, First" format).
        :return: Standardized author name in the "First Last" format.
        """
        # Trim leading/trailing whitespace and normalize to lowercase
        author_name = author_name.strip().lower()

        # Case 1: If the name is in "Last, First" format (e.g., "MOORE, T. C.")
        match = re.match(r"^([A-Za-z]+),\s*([A-Za-z]+(?:\s+[A-Za-z]+)?)\s*$", author_name)
        if match:
            last_name = match.group(1)
            first_name = match.group(2)
            # We standardize "T. C." as "Timothy C."
            first_name = " ".join([name.capitalize() for name in first_name.split()])
            return f"{first_name} {last_name}"

        # Case 2: If the name is already in "First Last" format (e.g., "Timothy C. Moore")
        # Normalize initials and spaces, and handle cases like "Wei H. Chen" or "Wei H Cheng"
        name_parts = author_name.split()

        # Standardize initials
        name_parts = [part.capitalize() if '.' not in part else part.capitalize() for part in name_parts]


        # If initials are present, treat the full name as "First Last" format
        return " ".join(name_parts)

    def get_publications_by_author(self, author_name, rows=10):
        """
        Retrieve publications from Elsevier by author name.
        :param author_name: The name of the author to search for
        :param rows: The number of results to return (default is 10)
        :return: A list of dictionaries containing publication details
        """
        if not author_name.strip():
            logging.warning("Received empty string for author name, skipping search.")
            return None

        # Normalize the author name
        normalized_name = self.normalize_author_name(author_name)

        # Prepare the query parameters
        params = {
            'query': f'AUTHOR-NAME({normalized_name})',
            'count': rows,
            'apiKey': self.api_key
        }

        # Send the request to the Elsevier API
        headers = {
            "Accept": "application/json"
        }

        # Send the request to the Springer API
        response = requests.get(self.base_url, headers=headers, params=params)

        # Check if the response was successful
        if response.status_code != 200:
            logging.error(f"Error fetching data from Elsevier API: {response.status_code}")
            return None

        # Log the raw response for debugging
        data = response.json()

        # Extract publication records
        publications = []
        for record in data.get('search-results', {}).get('entry', []):
            # Get basic publication details
            title = record.get('dc:title', 'No title available')
            publication_name = record.get('prism:publicationName', 'No journal available')
            publication_date = record.get('prism:coverDate', 'No date available')
            content_type = record.get('subtypeDescription', 'No type available')
            doi = record.get('prism:doi', 'No DOI available')

            # Get authors (ensure multiple authors are captured)
            authors = []
            if 'author' in record:
                for author in record['author']:
                    author_name = author.get('authname', '')
                    if author_name:
                        authors.append(author_name)
            elif 'dc:creator' in record:
                authors.append(record['dc:creator'])

            # Create a dictionary with the relevant information
            publication = {
                'doi': doi,
                'journal': publication_name,
                'content_type': content_type,
                'publication_date': publication_date,
                'title': title,
                'authors': ", ".join(authors),
            }
            publications.append(publication)
        
        return publications

def search_multiple_authors(api_key, authors, limit=10):
    """
    Search for publications by multiple authors.
    :param api_key: Elsevier API key
    :param authors: List of author names to search for
    :return: Dictionary with results for each author
    """
    elsevier_api = Elsevier(api_key)
    all_results = {}  # Dictionary to hold results for all authors

    for author in authors:
        print(f"Searching for publications by {author}...")
        if author == "":
            logging.warning("Received empty string for author name, continuing...")
            continue
        try:
            # Get publications for each author
            publications = elsevier_api.get_publications_by_author(author,rows=limit)
            all_results[author] = publications if publications else []
        except Exception as e:
            logging.error(f"Error fetching data for {author}: {e}")
            all_results[author] = []  # On error, return an empty list for the author

    return all_results

if __name__ == "__main__":
    # Get API key
    api_key = ""
    
    # Input: list of author names (comma-separated input)
    author_names = input("Enter author names (comma-separated): ").split(',')

    # Strip any leading/trailing whitespace
    author_names = [name.strip() for name in author_names]

    # Get results for all authors
    results = search_multiple_authors(api_key, author_names)

    # Output the results in JSON format
    print(json.dumps(results, indent=4))
