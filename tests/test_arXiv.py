import pytest
from pubscraper.APIClasses import arXiv

@pytest.fixture
def test_skip_empty_name():
    """Test that providing an empty author name returns an empty result."""
    results = arXiv.search_multiple_authors([""])
    assert results == {}


def test_no_input():
    """Test that providing no input returns an empty result."""
    results = arXiv.search_multiple_authors([])
    assert results == {}

def test_partial_empty_input():
    results = arXiv.search_multiple_authors(["albert", ""])
    assert len(results) == 1


def test_search_all_names():
    """Test searching for multiple author names returns expected number of results."""
    results = arXiv.search_multiple_authors(["albert", "joe", "allen"])
    assert len(results) == 3


def test_no_results():
    """Test that a name with no results returns None for that name."""
    results = arXiv.search_multiple_authors(["Magret O Adekunle"])
    assert results == {"Magret O Adekunle": []}


def test_initials_lastname():
    """Test searching with initials and last name finds a specific paper."""
    results = arXiv.search_multiple_authors(["Timothy C Moore"])
    publications_found = results["Timothy C Moore"]
    assert any("Derivation" in pub["title"] for pub in publications_found)


def test_fullname():
    """Test searching with full name finds a specific paper."""
    results = arXiv.search_multiple_authors(["Timothy C. Moore"])
    publications_found = results["Timothy C. Moore"]
    assert any("Derivation" in pub["title"] for pub in publications_found)


def test_result_parity_1():
    """Test that results are the same when searching with full name or initials."""
    results_one = arXiv.search_multiple_authors(["Timothy C. Moore"])
    results_two = arXiv.search_multiple_authors(["Timothy C Moore"])
    assert (results_one["Timothy C. Moore"] == results_two["Timothy C Moore"])


def test_limit_number_of_results():
    """Test that the number of results is limited when specified."""
    results = arXiv.search_multiple_authors(["Timothy C Moore"], 2)
    assert len(results["Timothy C Moore"]) == 2
