import requests
import xml.etree.ElementTree as ET
import json

class ArxivAPI:
    def __init__(self):
        """
        Initialize the arXiv API client.
        """
        self.base_url = "http://export.arxiv.org/api/query"
    
    def get_publications_by_author(self, author_name, start=0, max_results=10):
        """
        Retrieve publications from arXiv by author name.
        :param author_name: The name of the author to search for
        :param start: The start index of the search (default is 0)
        :param max_results: The number of results to return (default is 10)
        :return: A list of dictionaries containing publication details
        """
        # Prepare the query parameters
        params = {
            'search_query': f"au:{author_name}",
            'start': start,
            'max_results': max_results
        }

        # Send the request to the arXiv API
        response = requests.get(self.base_url, params=params)

        # Check if the request was successful
        if response.status_code != 200:
            raise Exception(f"Error fetching data from arXiv API: {response.status_code}")

        # Parse the XML response
        root = ET.fromstring(response.text)

        # Extract publication records
        publications = []
        for entry in root.findall("{http://www.w3.org/2005/Atom}entry"):
            paper = {
                'title': self.get_text(entry, "{http://www.w3.org/2005/Atom}title"),
                'publication_name': self.get_text(entry.find("{http://www.w3.org/2005/Atom}source"), "{http://www.w3.org/2005/Atom}title", "arXiv"),
                'publication_date': self.get_text(entry, "{http://www.w3.org/2005/Atom}published"),
                'content_type': self.get_text(entry, "{http://www.w3.org/2005/Atom}category", "preprint"),
                'doi': self.get_text(entry, "{http://arxiv.org/schemas/atom}doi", ""),
                'authors': [self.get_text(author, "{http://www.w3.org/2005/Atom}name") for author in entry.findall("{http://www.w3.org/2005/Atom}author")]
            }
            publications.append(paper)

        return publications

    def get_text(self, element, tag, default=""):
        """
        Safely extract text from an XML element, returning a default value if the element is not found.
        :param element: The XML element
        :param tag: The tag to search for
        :param default: The value to return if the tag is not found (default is "")
        :return: Text content or default value
        """
        if element is not None:
            found_element = element.find(tag)
            if found_element is not None:
                return found_element.text
        return default

def search_multiple_authors(authors, max_results=10):
    """
    Search for publications by multiple authors.
    :param authors: List of author names to search for
    :return: Dictionary with results for each author
    """
    arxiv_api = ArxivAPI()
    all_results = {}  # Dictionary to hold results for all authors

    for author in authors:
        print(f"Searching for publications by {author}...")
        try:
            # Get publications for each author
            publications = arxiv_api.get_publications_by_author(author, max_results=max_results)
            all_results[author] = publications
        except Exception as e:
            print(f"Error fetching data for {author}: {e}")
            all_results[author] = []

    return all_results

if __name__ == "__main__":
    # Input: list of author names (comma-separated input)
    author_names = input("Enter author names (comma-separated): ").split(',')
    
    # Strip any leading/trailing whitespace
    author_names = [name.strip() for name in author_names]
    
    # Get results for all authors
    results = search_multiple_authors(author_names)
    
    # Output the results in JSON format
    print(json.dumps(results, indent=4))