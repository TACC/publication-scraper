import pytest
from pubscraper.APIClasses import Springer

dummy_api_key = ""
@pytest.fixture
def test_skip_empty_name():
    """Test that providing an empty author name returns an empty result."""
    results = Springer.search_multiple_authors(dummy_api_key, [""])
    assert results == {}

def test_no_input():
    """Test that providing no input returns an empty result."""
    results = Springer.search_multiple_authors(dummy_api_key, [])
    assert results == {}

def test_partial_empty_input():
    """Test that if one author is empty, it skips that author."""
    results = Springer.search_multiple_authors(dummy_api_key, ["albert", ""])
    assert len(results) == 1

def test_search_all_names():
    """Test searching for multiple author names returns expected number of results."""
    results = Springer.search_multiple_authors(dummy_api_key, ["albert", "joe", "allen"])
    assert len(results) == 3

def test_no_results():
    """Test that a name with no results returns an empty list for that name."""
    results = Springer.search_multiple_authors(dummy_api_key, ["Magret O Adekunle"])
    assert results == {"Magret O Adekunle": []}

def test_initials_lastname():
    """Test searching with initials and last name finds a specific paper."""
    results = Springer.search_multiple_authors(dummy_api_key, ["Timothy C Moore"])
    publications_found = results["Timothy C Moore"]
    assert any("Historical Social Network Analysis and Early Financial Exchanges" in pub["title"] for pub in publications_found)

def test_fullname():
    """Test searching with full name finds a specific paper."""
    results = Springer.search_multiple_authors(dummy_api_key, ["Timothy C. Moore"])
    publications_found = results["Timothy C. Moore"]
    assert any("Historical Social Network Analysis and Early Financial Exchanges" in pub["title"] for pub in publications_found)

def test_result_parity():
    """Test that results are the same when searching with full name or initials."""
    results_one = Springer.search_multiple_authors(dummy_api_key, ["Timothy C. Moore"])
    results_two = Springer.search_multiple_authors(dummy_api_key, ["Timothy C Moore"])
    assert (results_one["Timothy C. Moore"] == results_two["Timothy C Moore"])

def test_limit_number_of_results():
    """Test that the number of results is limited when specified."""
    results = Springer.search_multiple_authors(dummy_api_key, ["Timothy C Moore"], limit = 2)
    assert len(results["Timothy C Moore"]) == 2
