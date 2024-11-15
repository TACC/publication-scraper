import requests
import json
import time
import logging

format_str=f'[%(asctime)s ] %(filename)s:%(funcName)s:%(lineno)s - %(levelname)s: %(message)s'
logging.basicConfig(level=logging.DEBUG, format=format_str)


class Publication:
    def __init__(self, journal, pub_date, title, authors):
        self.journal = journal,
        self.pub_date = pub_date,
        self.title = title,
        self.authors = authors


class PubMed:
    def __init__(self):
        self.search_url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi'
        self.summary_url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi'

    def get_UIDs_by_author(self, author_name, rows=10):
        """
        Retrieve a given author's UID publications.
        :param author_name: name of author {firstName} {lastName}
        :param rows: number of results to return (default is 10)
        :return: A list of UIDs corresponding to papers written by the author
        """
        # prepare Entrez query
        if author_name == "":
            logging.warning("get_UIDs_by_author received an empty string for author search!")
            return None

        # PubMed searches by {lastName} {firstInitial}{midInitial}
        # searching by {firstName} {lastName} will always yield no results!
        split_name = author_name.split()
        if len(split_name) == 1:
            entrez_author_name = split_name[0] + "[author]"
        else:
            entrez_author_name = split_name[-1] + "+"
            for name in split_name[:-1]:
                entrez_author_name += "{initial}".format(initial = name[0])
            # entrez_author_name = author_name.replace(" ", "+")
            entrez_author_name += "[Author Name]"
        logging.info(f'searching for publications by {entrez_author_name}')

        params = {
            'db':'pmc',
            'term': entrez_author_name,
            'retmax': rows,
            'retmode': 'JSON',
        }

        response = requests.get(self.search_url, params=params)

        if response.status_code != 200:
            logging.error(f'Error fetching data from PubMed: {response.status_code}')
            # print(f"Error fetching data from PubMed: {response.status_code}")
            return None

        data = response.json()
        logging.debug(json.dumps(data, indent=2))
        id_list = data['esearchresult']['idlist']

        if not id_list:
            logging.warning(f"Received no UIDs for author {author_name}, returning None")
            logging.debug(f'passed "{entrez_author_name}" to PubMed API')
            return None

        logging.debug(f"received the following UIDs: {id_list}")
        return id_list

    def get_summary_by_UIDs(self, UIDs):
        """
        Given a list of UIDs, retrieve summary information for each UID
        :params UIDs: a list of UIDs
        :return: a list of Publication instances holding summary data for each publication
        """
        if not UIDs:
            return None
        
        # join UIDs list into one 'csv' string
        stringified_UIDs = ','.join(UIDs)
        params = {
            'db': 'pmc',
            'id': stringified_UIDs,
            'retmode': 'JSON',
        }

        response = requests.get(self.summary_url, params=params)
        if response.status_code != 200:
            print(f'Error fetching summaries from PubMed: {response.status_code}')
            return

        data = response.json()

        publications = []
        for uid in data['result']['uids']:
            summary_object = data['result'][uid]
            author_list = []
            for author_object in summary_object['authors']:
                author_list.append(author_object['name'])

            # pub = Publication(
            #     journal=summary_object['fulljournalname'],
            #     pub_date=summary_object['sortdate'],
            #     title=summary_object['title'],
            #     authors=author_list
            # )
            pub = {
                'id': uid,
                'journal': summary_object['fulljournalname'],
                'publication_date': summary_object['sortdate'],
                'title': summary_object['title'],
                'authors': ",".join(author_list)
            }
            publications.append(pub)

        return publications


    def get_publications_by_author(self, author_name, rows=10):
        UIDs = self.get_UIDs_by_author(author_name, rows)
        summary_info = self.get_summary_by_UIDs(UIDs)

        return summary_info


def search_multiple_authors(authors):
    pubmed = PubMed()
    all_results = {}

    for author in authors:
        print(f"Searching for publications by {author}...")

        if author == "":
            continue

        try:
            publications = pubmed.get_publications_by_author(author)
            all_results[author] = publications
        except Exception as e:
            print(f"Error fetching data for {author}: {e}")
        time.sleep(0.4)    # avoids RESPONSE 429 (rate limit violation)

    return all_results

def main():
    # authors = ['albert', 'albert einstein', 'albert einsten']
    # authors = ['albert einstein']
    author_names = input("Enter author names (comma-separated): ").split(",")
    author_names = [name.strip() for name in author_names]

    results = search_multiple_authors(author_names)
    print(json.dumps(results, indent=2))


if __name__ == '__main__':
    main()
