import json
from APIClasses.PubMed import PubMed
from APIClasses.arXiv import ArxivAPI


def main():
    author_names = input("Enter author names(comma-separated): ").split(",")
    author_names = [name.strip() for name in author_names]

    apis = [PubMed(), ArxivAPI()]
    authors_and_pubs = []

    for author in author_names:
        results = {author: []}
        # FIXME: these names are too similar and confusing
        authors_pubs = []
        for api in apis:
            pubs_found = api.get_publications_by_author(author)
            if pubs_found is not None:
                authors_pubs += pubs_found

            results.update({author: authors_pubs})

        authors_and_pubs.append(results)

    print(json.dumps(authors_and_pubs, indent=2))
    return authors_and_pubs


if __name__ == "__main__":
    main()
