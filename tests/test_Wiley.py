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
