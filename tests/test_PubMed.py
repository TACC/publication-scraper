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


def test_should_fail():
    pb = PubMed.PubMed()
    with pytest.raises(Exception):
        pb.get_UIDs_by_author("w j allen", -1)


def test_bad_author_name():
    pb = PubMed.PubMed()
    result = pb.get_UIDs_by_author("")
    assert result is None


def test_HTTP_failure_UIDs():
    pb = PubMed.PubMed()
    pb.search_url = "https://httpstat.us/500"
    result = pb.get_UIDs_by_author("joe hendrix", 1)
    assert result is None


def test_HTTP_failure_summaries():
    pb = PubMed.PubMed()
    pb.summary_url = "https://httpstat.us/500"
    result = pb.get_summary_by_UIDs(["12345"])
    assert result is None


def test_failure_multiple_authors():
    empty_results = PubMed.search_multiple_authors(["kelsey", "erik"], -1)
    assert empty_results == {}


def test_same_response():
    result_one = PubMed.search_multiple_authors(["joe hendrix"])
    result_two = PubMed.search_multiple_authors(["joe hendrix"])
    assert result_one == result_two
