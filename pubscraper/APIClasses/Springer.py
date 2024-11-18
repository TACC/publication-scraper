import requests
import json

class Springer:
    def __init__(self, api_key):
        """
        Initialize the Springer (springernature) API client.
        :param api_key: Your Springer API key
        """
        self.base_url = "https://api.springernature.com/openaccess/json"
        self.api_key = api_key


    def get_publications_by_author(self, author_name, rows=10):
        """
        Retrieve publications from Springer by author name.
        :param author_name: The name of the author to search for
        :param rows: The number of results to return (default is 10)
        :return: A list of dictionaries containing publication details
        """
        # Prepare the query parameters
        params = {
            'q': author_name,
            'p': rows,
            'api_key': self.api_key
        }

        # Send the request to the Springer API
        response = requests.get(self.base_url, params=params)

        # Check if the request was successful
        if response.status_code != 200:
            raise Exception(f"Error fetching data from Springer API: {response.status_code}")

        # Parse the JSON response
        data = response.json()

        # Extract publication records
        publications = []
        for record in data.get('records', []):
            # Get basic publication details
            title = record.get('title', 'No title available')
            publication_name = record.get('publicationName', 'No journal available')
            publication_date = record.get('publicationDate', 'No date available')
            content_type = record.get('contentType', 'No type available')
            doi = record.get('doi', 'No DOI available')
            
            # Get authors (Springer API returns creators differently)
            creators = record.get('creators', [])
            authors = [creator.get('creator', '') for creator in creators]

            # Create a dictionary with the relevant information
            if all([title, authors, publication_date, publication_name]):
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

def search_multiple_authors(api_key, authors):
    """
    Search for publications by multiple authors.
    :param api_key: Springer API key
    :param authors: List of author names to search for
    :return: Dictionary with results for each author
    """
    springer_api = Springer(api_key)
    all_results = {}  # Dictionary to hold results for all authors

    for author in authors:
        print(f"Searching for publications by {author}...")
        try:
            # Get publications for each author
            publications = springer_api.get_publications_by_author(author)
            all_results[author] = publications
        except Exception as e:
            print(f"Error fetching data for {author}: {e}")

    return all_results

if __name__ == "__main__":
    # Get API key
    api_key = input("Enter your Springer API key: ")
    
    # Input: list of author names (comma-separated input)
    author_names = input("Enter author names (comma-separated): ").split(',')
    
    # Strip any leading/trailing whitespace
    author_names = [name.strip() for name in author_names]
    
    # Get results for all authors
    results = search_multiple_authors(api_key, author_names)
    
    # Output the results in JSON format
    print(json.dumps(results, indent=4))