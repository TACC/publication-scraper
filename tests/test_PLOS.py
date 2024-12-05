import pytest
import responses
from pubscraper.APIClasses import PLOS
import logging
import json

logging.basicConfig(level=logging.DEBUG)

BASE_URL = "https://api.plos.org/search"


@pytest.fixture
def mock_api():
    with responses.RequestsMock() as rsps:
        yield rsps


def mock_PLOS_response(entries):
    """Helper function to generate mock JSON response."""
    return {"feed": {"entries": entries}}


def test_skip_empty_name(mock_api):
    """Test skipping empty author names."""
    results = PLOS.search_multiple_authors([""])
    assert results == {}
    assert len(mock_api.calls) == 0  # No requests should have been made


def test_no_input(mock_api):
    """Test that providing no input returns an empty result."""
    results = PLOS.search_multiple_authors([])
    assert results == {}
    assert len(mock_api.calls) == 0  # No requests should have been made


def test_partial_empty_input(mock_api):
    """Test handling of partial empty input in author list."""

    # Mock response for "albert"
    mock_api.add(
        responses.GET,
        BASE_URL,
        match=[
            responses.matchers.query_param_matcher(
                {"q": 'author:"Albert"', "rows": "10", "wt": "json"}
            )
        ],
        body=mock_PLOS_response(
            [
                {
                    "title": "Sample Paper",
                    "author": [{"name": "Albert"}],
                    "published": "2024-01-01",
                }
            ]
        ),
        status=200,
    )
    results = PLOS.search_multiple_authors(["Albert", ""])

    assert len(results) == 1
    assert "Albert" in results
    assert len(mock_api.calls) == 1


def test_search_all_names(mock_api):
    mock_api.add(
        responses.GET,
        BASE_URL,
        match=[
            responses.matchers.query_param_matcher(
                {"q": 'author:"Albert"', "rows": "10", "wt": "json"}
            )
        ],
        body=mock_PLOS_response(
            [
                {
                    "title": "Sample Paper",
                    "author": [{"name": "Albert"}],
                    "published": "2024-01-01",
                }
            ]
        ),
        status=200,
    )
    mock_api.add(
        responses.GET,
        BASE_URL,
        match=[
            responses.matchers.query_param_matcher(
                {"q": 'author:"Joe"', "rows": "10", "wt": "json"}
            )
        ],
        body=mock_PLOS_response(
            [
                {
                    "title": "Sample Paper",
                    "author": [{"name": "Joe"}],
                    "published": "2024-01-01",
                }
            ]
        ),
        status=200,
    )
    mock_api.add(
        responses.GET,
        BASE_URL,
        match=[
            responses.matchers.query_param_matcher(
                {"q": 'author:"Allen"', "rows": "10", "wt": "json"}
            )
        ],
        body=mock_PLOS_response(
            [
                {
                    "title": "Sample Paper",
                    "author": [{"name": "Allen"}],
                    "published": "2024-01-01",
                }
            ]
        ),
        status=200,
    )

    results = PLOS.search_multiple_authors(["Albert", "Joe", "Allen"])
    assert len(results) == 3
    assert "Albert" in results
    assert "Joe" in results
    assert "Allen" in results


def test_no_results_for_name(mock_api):
    """Test that an author with no results returns None."""
    mock_api.add(
        responses.GET,
        BASE_URL,
        match=[
            responses.matchers.query_param_matcher(
                {"q": 'author:"Magert O. Adekunle"', "rows": "10", "wt": "json"}
            )
        ],
        body=mock_PLOS_response([]),
        status=200,
    )

    results = PLOS.search_multiple_authors(["Magert O. Adekunle"])
    assert results.get("Magert O. Adekunle") == []


def test_limit_number_of_results(mock_api):
    """Test limiting the number of results using `rows`."""
    mock_api.add(
        responses.GET,
        BASE_URL,
        match=[
            responses.matchers.query_param_matcher(
                {"q": 'author:"Timothy C. Moore"', "rows": "2", "wt": "json"}
            )
        ],
        body=json.dumps({
            "response": {
                "docs": [
                    {
                        "id": "doi1",
                        "title_display": "Sample Paper 1",
                        "author_display": ["Allen"],
                        "publication_date": "2024-01-01",
                        "journal": "Sample Journal",
                        "article_type": "Research Article"
                    },
                    {
                        "id": "doi2",
                        "title_display": "Sample Paper 2",
                        "author_display": ["Allen"],
                        "publication_date": "2024-01-01",
                        "journal": "Sample Journal",
                        "article_type": "Research Article"
                    }
                ]
            }
        }),
        status=200,
        content_type="application/json"
    )
    
    results = PLOS.search_multiple_authors(["Timothy C. Moore"], rows=2)
    assert len(results["Timothy C. Moore"]) == 2