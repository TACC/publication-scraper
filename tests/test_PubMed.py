import pytest
from pubscraper.APIClasses import PubMed

def test_skip_empty_name():
    results = PubMed.search_multiple_authors([""])
    assert results == {}


def test_no_input():
    results = PubMed.search_multiple_authors([])
    assert results == {}


def test_partial_empty_input():
    results = PubMed.search_multiple_authors(["albert", ""])
    assert len(results) == 1


def test_search_all_names():
    results = PubMed.search_multiple_authors(["albert", "joe", "allen"])
    assert len(results) == 3


def test_no_results():
    results = PubMed.search_multiple_authors(["joseph l hendrix"])
    assert results == {"joseph l hendrix": None}


def test_initials_lastname():
    results = PubMed.search_multiple_authors(["w j allen"])
    publications_found = results["w j allen"]
    # iterate through publications_found to find a paper authored by Joe Allen
    biasnet_found = False
    for pub in publications_found:
        if "BiasNet" in pub["title"]:
            biasnet_found = True
    assert biasnet_found


def test_fullname():
    results = PubMed.search_multiple_authors(["william joseph allen"])
    publications_found = results["william joseph allen"]
    # iterate thorugh publications_found to find a paper authored by Joe Allen
    biasnet_found = False
    for pub in publications_found:
        if "BiasNet" in pub["title"]:
            biasnet_found = True
    assert biasnet_found


def test_result_parity():
    results_one = PubMed.search_multiple_authors(["william joseph allen"])
    results_two = PubMed.search_multiple_authors(["w j allen"])
    pubs_found_one = results_one["william joseph allen"]
    pubs_found_two = results_two["w j allen"]
    assert pubs_found_one == pubs_found_two


def test_limit_number_of_results():
    results = PubMed.search_multiple_authors(["w j allen"], 2)
    assert len(results["w j allen"]) == 2
