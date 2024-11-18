import requests
import json

class Elsevier:
    def __init__(self, api_key):
        """
        Initialize the Elsevier API client.
        :param api_key: Your Elsevier API key
        """
        self.base_url = "https://api.elsevier.com/content/search/scopus"
        self.api_key = api_key

    def get_publications_by_author(self, author_name, rows=10):
        """
        Retrieve publications from Elsevier by author name.
        :param author_name: The name of the author to search for
        :param rows: The number of results to return (default is 10)
        :return: A list of dictionaries containing publication details
        """
        # Prepare the query parameters
        params = {
            'query': f'AUTHOR-NAME({author_name})',
            'count': rows,
            'apiKey': self.api_key
        }

        # Send the request to the Elsevier API
        headers = {
            "Accept": "application/json"
        }
        response = requests.get(self.base_url, headers=headers, params=params)

        # Check if the request was successful
        if response.status_code != 200:
            raise Exception(f"Error fetching data from Elsevier API: {response.status_code}")

        # Parse the JSON response
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

def search_multiple_authors(api_key, authors):
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
        try:
            # Get publications for each author
            publications = elsevier_api.get_publications_by_author(author)
            all_results[author] = publications
        except Exception as e:
            print(f"Error fetching data for {author}: {e}")

    return all_results

if __name__ == "__main__":
    # Get API key
    api_key = input("Enter your Elsevier API key: ")

    # Input: list of author names (comma-separated input)
    author_names = input("Enter author names (comma-separated): ").split(',')

    # Strip any leading/trailing whitespace
    author_names = [name.strip() for name in author_names]

    # Get results for all authors
    results = search_multiple_authors(api_key, author_names)

    # Output the results in JSON format
    print(json.dumps(results, indent=4))