import requests
import json
import re
import logging

# Set up basic logging
format_str = "[%(asctime)s] %(filename)s:%(funcName)s:%(lineno)d - %(levelname)s: %(message)s"
logging.basicConfig(level=logging.DEBUG, format=format_str)

class Wiley:
    def __init__(self, api_key):
        """
        Initialize the Wiley Online Library API client.
        :param api_key: Your Wiley API key
        """
        self.base_url = "https://api.wiley.com/api/v1/articles" 
        self.api_key = api_key

    def normalize_author_name(self, author_name):
        """
        Normalize author name to the most consistent format for querying the Springer API.
        :param author_name: Author's name (either in "First Last" or "Last, First" format).
        :return: Standardized author name in the "First Last" format.
        """
        # Trim leading/trailing whitespace
        author_name = author_name.strip()
        
        # Case 1: If the name is in "Last, First" format (e.g., "MOORE, T. C.")
        match = re.match(r"^([A-Za-z]+),\s*([A-Za-z]+(?:\s+[A-Za-z]+)?)\s*(.*)$", author_name)
        if match:
            last_name = match.group(1)
            first_name = match.group(2)
            # We standardize "T. C." as "Timothy C."
            first_name = " ".join([name.capitalize() for name in first_name.split()])
            return f"{first_name} {last_name}"

        # Case 2: If the name is already in "First Last" format (e.g., "Timothy C. Moore")
        # Just return the name as is, with proper capitalization
        return " ".join([name.capitalize() for name in author_name.split()])
    

    def get_publications_by_author(self, author_name, rows=10):
        """
        Retrieve publications from Springer by author name, with flexible search options.
        :param author_name: The name of the author to search for (full name, initials, etc.)
        :param rows: The number of results to return (default is 10)
        :return: A list of dictionaries containing publication details
        """
        if author_name.strip() == "":
            logging.warning("Received empty string for author name in search query, returning None")
            return None

        # Normalize the author name before querying
        normalized_name = self.normalize_author_name(author_name)

        # Prepare the query parameters
        params = {
            'author': normalized_name,
            'count': rows,
        }

        # Set the headers with the API key for authentication
        headers = {
            'Authorization': f'Bearer {self.api_key}'
        }

        # Send the request to the Wiley API
        response = requests.get(self.base_url, params=params, headers=headers)

        # Check if the request was successful
        if response.status_code != 200:
            logging.error(f"Error fetching data from Springer API: {response.status_code}")
            return None

        # Parse the JSON response
        data = response.json()

        # Extract publication records
        publications = []
        for record in data.get('articles', []):
            # Get basic publication details
            title = record.get('title', 'No title available')
            publication_name = record.get('journalTitle', 'No journal available')
            publication_date = record.get('publicationDate', 'No date available')
            doi = record.get('doi', 'No DOI available')
            
            # Get authors
            authors = ", ".join(record.get('authorList', []))

            # Create a dictionary with the relevant information
            if all([title, authors, publication_date, publication_name]):
                publication = {
                    'doi': doi,
                    'journal': publication_name,
                    'publication_date': publication_date,
                    'title': title,
                    'authors': authors,
                }
                publications.append(publication)

        return publications

def search_multiple_authors(api_key, authors, limit=10):
    """
    Search for publications by multiple authors.
    :param api_key: Wiley API key
    :param authors: List of author names to search for
    :return: Dictionary with results for each author
    """
    wiley_api = Wiley(api_key)
    all_results = {}  # Dictionary to hold results for all authors

    for author in authors:
        print(f"Searching for publications by {author}...")
        if author == "":
            logging.warning("Received empty string for author name, continuing...")
            continue
        try:
            # Get publications for each author
            publications = wiley_api.get_publications_by_author(author)
            all_results[author] = publications
        except Exception as e:
            logging.error(f"Error fetching data for {author}: {e}")

    return all_results

if __name__ == "__main__":
    # Get API key
    api_key = input("Enter your Wiley API key: ")
    
    # Input: list of author names (comma-separated input)
    author_names = input("Enter author names (comma-separated): ").split(',')
    
    # Strip any leading/trailing whitespace
    author_names = [name.strip() for name in author_names]
    
    # Get results for all authors
    results = search_multiple_authors(api_key, author_names)
    
    # Output the results in JSON format
    print(json.dumps(results, indent=4))