import pytest
import responses
from responses import _recorder

from pubscraper.APIClasses import Wiley


def test_empty_name():
    results = Wiley.search_multiple_authors([""])
    assert results == {}


def test_skip_no_input():
    results = Wiley.search_multiple_authors([])
    assert results == {}


@responses.activate
def test_partial_empty_input():
    responses._add_from_file(file_path="tests/Wiley_out.yaml")
    results = Wiley.search_multiple_authors(["albert", ""])
    assert len(results) == 1


def test_search_all_name():
    responses._add_from_file(file_path="tests/Wiley_out.yaml")
    results = Wiley.search_multiple_authors(["william", "joe", "allen"])
    assert len(results) == 3


@responses.activate
def test_no_results():
    responses._add_from_file(file_path="tests/Wiley_out.yaml")
    results = Wiley.search_multiple_authors(["gibberish noneresults"])
    assert results == {"gibberish noneresults": []}


@responses.activate
def test_limit_number_of_results():
    responses._add_from_file(file_path="tests/Wiley_out.yaml")
    results = Wiley.search_multiple_authors(["richard feynman"], 2)
    assert len(results["richard feynman"]) == 2


@responses.activate
def test_bad_author_name():
    wiley = Wiley.Wiley()
    result = wiley._get_publications_by_author("")
    assert result is None


@responses.activate
def test_HTTP_failure():
    response_1 = responses.Response(
        method="GET", url="https://onlinelibrary.wiley.com/action/sru", status=500
    )
    responses.add(response_1)
    result = Wiley.search_multiple_authors(["some author"])
    assert result == {"some author": []}
