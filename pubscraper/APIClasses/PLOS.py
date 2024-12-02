import requests
import json
import logging

format_str = "[%(asctime)s] %(filename)s:%(funcName)s:%(lineno)d - %(levelname)s: %(message)s"
logging.basicConfig(level=logging.DEBUG, format=format_str)

class PLOS:
    def __init__(self):
        self.base_url = "https://api.plos.org/search"

    def get_publications_by_author(self, author_name, rows=10):
        """"
        Retrieve publications from PLOS by author name.

        :param author_name: The name of the author to search for
        :param rows: The number of results to return (default is 10)
        :return: A list of dictionaries containing publication details
        """
        if author_name.strip() == "":
            logging.warning("Received empty string for author name in search query, returning None")
            return None
    
        # Prepare the query parameters
        params = {
            'q': f'author:"{author_name}"',
            'rows': rows,
            'wt': 'json'
        }

        # Error handling when interacting with PLOS APIs.
        try:
            response = requests.get(self.base_url, params=params, timeout=10)  # Send the request to the PLOS API
            response.raise_for_status()  # Raises HTTP Error for bad responses
        except requests.exceptions.RequestException as e:
            logging.error(f"Elsevier API Request error: {e}")
            return None
        
    
        # Parse the JSON response
        data = response.json()

        # Extract publication records
        publications = []
        for doc in data['response']['docs']:
            doi = doc.get('id', 'No ID available')
            journal = doc.get('journal', 'No journal available')
            article_type = doc.get('article_type', 'No article type available')
            publication_date = doc.get('publication_date', 'No date available')
            title = doc.get('title_display', 'No title available')
            authors = doc.get('author_display', [])

            # Create a dictionary with the relevant information
            if all([title, authors, publication_date, journal]):
                publication = {
                    'doi': doi,
                    'journal': journal,
                    'article_type': article_type,
                    'publication_date': publication_date,
                    'title': title,
                    'authors': ", ".join(authors),
                }
                publications.append(publication)

        return publications

# Function to search for multiple authors
def search_multiple_authors(authors):
    plos_api = PLOS()
    all_results = {} # Dictionary to hold results for all authors

    for author in authors:
        print(f"Searching for publications by {author}...")
        if author == "":
            logging.warning("Received empty string for author name, continuing...")
            continue
        try:
            # Get publications for each author
            publications = plos_api.get_publications_by_author(author)
            all_results[author] = publications
        except Exception as e:
            print(f"Error fetching data for {author}: {e}")
    
    return all_results

# Example usage
if __name__ == "__main__":
    # Input: list of author names (comma-separated input)
    author_names = input("Enter author names (comma-separated): ").split(',')

    # Strip any leading/trailing whitespace
    author_names = [name.strip() for name in author_names]

    # Get results for all authors
    results = search_multiple_authors(author_names)

    # Output the results in JSON format
    print(json.dumps(results, indent=4))