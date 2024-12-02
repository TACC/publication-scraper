LOGGER_FORMAT_STRING = (
    "[%(asctime)s] %(filename)s:%(funcName)s:%(lineno)d - %(levelname)s: %(message)s"
)
LOGGER_LEVEL = "INFO"

ELSEVIER_URL = "https://api.elsevier.com/content/search/scopus"
IEEE_URL = "https://ieeexplore.ieee.org/api/v1/search/articles"
MDPI_URL = "https://api.mdpi.com/v1/articles"
PUBMED_SEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
PUBMED_SUMMARY_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
SPRINGER_URL = "https://api.springernature.com/openaccess/json"
WILEY_URL = "https://onlinelibrary.wiley.com/action/sru"
ARXIV_URL = "http://export.arxiv.org/api/query"
PLOS_URL = "https://api.plos.org/search"

API_LIST = ["Elsevier", "IEEE", "MDPI", "PubMed", "Springer", "Wiley", "arXiv", "PLOS"]
