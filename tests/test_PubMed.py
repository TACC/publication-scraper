import pytest
import responses
from responses import _recorder

from pubscraper.APIClasses import PubMed


def test_skip_empty_name():
    results = PubMed.search_multiple_authors([""])
    assert results == {}


def test_no_input():
    results = PubMed.search_multiple_authors([])
    assert results == {}


@responses.activate
def test_partial_empty_input():
    response_1 = responses.Response(
        method="GET",
        url="https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
        status=200,
        json={"esearchresult": {"idlist": ["12345678"]}},
    )
    responses.add(response_1)
    response_2 = responses.Response(
        method="GET",
        url="https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi",
        status=200,
        json={
            "result": {
                "uids": ["12345678"],
                "12345678": {
                    "authors": [{"name": "albert"}],
                    "title": "some title",
                    "fulljournalname": "some journal",
                    "sortdate": "2000/09/06",
                },
            }
        },
    )
    responses.add(response_2)
    results = PubMed.search_multiple_authors(["albert", ""])
    assert len(results) == 1


@responses.activate
def test_search_all_names():
    response_1 = responses.Response(
        method="GET",
        url="https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
        status=200,
        json={"esearchresult": {"idlist": ["12345678"]}},
    )
    responses.add(response_1)
    response_2 = responses.Response(
        method="GET",
        url="https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi",
        status=200,
        json={
            "result": {
                "uids": ["12345678"],
                "12345678": {
                    "authors": [{"name": "albert"}],
                    "title": "some title",
                    "fulljournalname": "some journal",
                    "sortdate": "2000/09/06",
                },
            }
        },
    )
    responses.add(response_2)
    response_3 = responses.Response(
        method="GET",
        url="https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
        status=200,
        json={"esearchresult": {"idlist": ["12345678"]}},
    )
    responses.add(response_3)
    response_4 = responses.Response(
        method="GET",
        url="https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi",
        status=200,
        json={
            "result": {
                "uids": ["12345678"],
                "12345678": {
                    "authors": [{"name": "joe"}],
                    "title": "some title",
                    "fulljournalname": "some journal",
                    "sortdate": "2000/09/06",
                },
            }
        },
    )
    responses.add(response_4)
    response_5 = responses.Response(
        method="GET",
        url="https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
        status=200,
        json={"esearchresult": {"idlist": ["12345678"]}},
    )
    responses.add(response_5)
    response_6 = responses.Response(
        method="GET",
        url="https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi",
        status=200,
        json={
            "result": {
                "uids": ["12345678"],
                "12345678": {
                    "authors": [{"name": "allen"}],
                    "title": "some title",
                    "fulljournalname": "some journal",
                    "sortdate": "2000/09/06",
                },
            }
        },
    )
    responses.add(response_6)

    results = PubMed.search_multiple_authors(["albert", "joe", "allen"])
    assert len(results) == 3


@responses.activate
def test_no_results():
    response_1 = responses.Response(
        method="GET",
        url="https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
        status=200,
        json={"esearchresult": {"idlist": []}},
    )
    responses.add(response_1)
    results = PubMed.search_multiple_authors(["joseph l hendrix"])
    assert results == {"joseph l hendrix": None}


@responses.activate
def test_initials_lastname():
    response_1 = responses.Response(
        method="GET",
        url="https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
        status=200,
        json={"esearchresult": {"idlist": ["12345678"]}},
    )
    responses.add(response_1)
    response_2 = responses.Response(
        method="GET",
        url="https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi",
        status=200,
        json={
            "result": {
                "uids": ["12345678"],
                "12345678": {
                    "authors": [{"name": "w j allen"}],
                    "title": "BiasNet",
                    "fulljournalname": "some journal",
                    "sortdate": "2000/09/06",
                },
            }
        },
    )
    responses.add(response_2)

    results = PubMed.search_multiple_authors(["w j allen"])
    publications_found = results["w j allen"]
    # iterate through publications_found to find a paper authored by Joe Allen
    biasnet_found = False
    for pub in publications_found:
        if "BiasNet" in pub["title"]:
            biasnet_found = True
    assert biasnet_found


@responses.activate
def test_fullname():
    response_1 = responses.Response(
        method="GET",
        url="https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
        status=200,
        json={"esearchresult": {"idlist": ["12345678"]}},
    )
    responses.add(response_1)
    response_2 = responses.Response(
        method="GET",
        url="https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi",
        status=200,
        json={
            "result": {
                "uids": ["12345678", "23456789"],
                "12345678": {
                    "authors": [{"name": "william joseph allen"}],
                    "title": "BiasNet",
                    "fulljournalname": "some journal",
                    "sortdate": "2000/09/06",
                },
                "23456789": {
                    "authors": [{"name": "william joseph allen"}],
                    "title": "BiasNet",
                    "fulljournalname": "some journal",
                    "sortdate": "2000/09/06",
                },
            }
        },
    )
    responses.add(response_2)

    results = PubMed.search_multiple_authors(["william joseph allen"])
    publications_found = results["william joseph allen"]
    # iterate thorugh publications_found to find a paper authored by Joe Allen
    biasnet_found = False
    for pub in publications_found:
        if "BiasNet" in pub["title"]:
            biasnet_found = True
    assert biasnet_found


@responses.activate
def test_limit_number_of_results():
    response_1 = responses.Response(
        method="GET",
        url="https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
        status=200,
        json={"esearchresult": {"idlist": ["12345678", "12345678"]}},
    )
    responses.add(response_1)
    response_2 = responses.Response(
        method="GET",
        url="https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi",
        status=200,
        json={
            "result": {
                "uids": ["12345678", "23456789"],
                "12345678": {
                    "authors": [{"name": "w j allen"}],
                    "title": "BiasNet",
                    "fulljournalname": "some journal",
                    "sortdate": "2000/09/06",
                },
                "23456789": {
                    "authors": [{"name": "w j allen"}],
                    "title": "BiasNet",
                    "fulljournalname": "some journal",
                    "sortdate": "2000/09/06",
                },
            }
        },
    )
    responses.add(response_2)

    results = PubMed.search_multiple_authors(["w j allen"], 2)
    assert len(results["w j allen"]) == 2


def test_should_fail():
    pb = PubMed.PubMed()
    with pytest.raises(Exception):
        pb._get_UIDs_by_author("w j allen", -1)


def test_bad_author_name():
    pb = PubMed.PubMed()
    result = pb._get_UIDs_by_author("")
    assert result is None


@responses.activate
def test_HTTP_failure_UIDs():
    response_1 = responses.Response(
        method="GET", url="https://httpstat.us/500", status=500
    )
    responses.add(response_1)
    pb = PubMed.PubMed()
    pb.search_url = "https://httpstat.us/500"
    result = pb._get_UIDs_by_author("joe hendrix", 1)
    assert result is None


@responses.activate
def test_HTTP_failure_summaries():
    response_1 = responses.Response(
        method="GET",
        url="https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
        status=200,
        json={"esearchresult": {"idlist": ["12345678", "12345678"]}},
    )
    responses.add(response_1)
    response_2 = responses.Response(
        method="GET",
        url="https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi",
        status=500,
    )
    responses.add(response_2)

    result = PubMed.search_multiple_authors(["some author"])
    assert result == {}


def test_failure_multiple_authors():
    empty_results = PubMed.search_multiple_authors(["kelsey", "erik"], -1)
    assert empty_results == {}
