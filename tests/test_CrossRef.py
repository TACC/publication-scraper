import pytest
import json
import os
from pubscraper.APIClasses import CrossRef


def test_skip_empty_name():
    results = CrossRef.search_multiple_authors([""])
    assert results == {}


def test_no_input():
    results = CrossRef.search_multiple_authors([])
    assert results == {}


def test_partial_empty_input():
    results = CrossRef.search_multiple_authors(["albert", ""])
    assert len(results) == 1


def test_search_all_names():
    results = CrossRef.search_multiple_authors(["albert", "joe", "allen"])
    assert len(results) == 3


def test_no_results():
    results = CrossRef.search_multiple_authors(["gibberish noneresults"])
    assert results == {"gibberish noneresults": None}


def test_limit_results():
    results = CrossRef.search_multiple_authors(["nothing nothing"])
    assert len(results["nothing nothing"]) < 10


def test_author_retry():
    results = CrossRef.search_multiple_authors(["j l hendrix"])
    # requesting 10 valid results for "j l hendrix" will provoke a KeyError
    # when searching for author["family"]
    assert len(results["j l hendrix"]) == 10


def test_should_fail():
    cr = CrossRef.CrossRef()
    with pytest.raises(Exception):
        cr.get_publications_by_author("j l hendrix", -1)


def test_HTTP_failure():
    cr = CrossRef.CrossRef()
    cr.base_url = "https://httpstat.us/500"
    result = cr.get_publications_by_author("j l hendrix")
    assert result is None


def test_result_parity():
    # this test sometimes fails, I have no idea why
    try:
        os.remove("results_one.json")
    except Exception:
        pass

    try:
        os.remove("results_two.json")
    except Exception:
        pass

    result_one = CrossRef.search_multiple_authors(["richard feynman"])
    result_two = CrossRef.search_multiple_authors(["richard feynman"])
    with open("results_one.json", "w") as fout:
        fout.writelines(json.dumps(result_one, indent=2))

    with open("results_two.json", "w") as fout:
        fout.writelines(json.dumps(result_two, indent=2))

    assert result_one == result_two
