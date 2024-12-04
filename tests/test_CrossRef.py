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
