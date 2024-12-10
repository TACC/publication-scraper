import pytest
import responses
import logging
import json

from pubscraper.APIClasses import Elsevier

logging.basicConfig(level=logging.DEBUG)

BASE_URL = "https://api.elsevier.com/content/search/scopus"

with open("secrets.json") as f:
    secrets = json.load(f)
    api_key = secrets["Elsevier"]

@pytest.fixture
def mock_api():
    with responses.RequestsMock() as rsps:
        yield rsps


def mock_Elsevier_response(entries):
    """Helper function to generate mock JSON response."""
    return {"feed": {"entries": entries}}


def test_skip_empty_name(mock_api):
    """Test skipping empty author names."""
    results = Elsevier.search_multiple_authors([""])
    assert results == {}
    assert len(mock_api.calls) == 0  # No requests should have been made


def test_no_input(mock_api):
    """Test that providing no input returns an empty result."""
    results = Elsevier.search_multiple_authors([])
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
                {"query": "AUTHOR-NAME(Albert)", "count": "10", "apiKey": api_key}
            )
        ],
        body=mock_Elsevier_response(
            [
                {
                    "prism:doi": "doi1",
                    "dc:title": "Sample Paper 1",
                    "prism:coverDate": "2024-01-01",
                    "prism:publicationName": "Sample Journal",
                    "subtypeDescription": "Research Article",
                    "author": [{"authname": "Albert"}],                     
                }
            ]
        ),
        status=200,
    )
    results = Elsevier.search_multiple_authors(["Albert", ""])

    assert len(results) == 1
    assert "Albert" in results
    assert len(mock_api.calls) == 1


def test_search_all_names(mock_api):
    mock_api.add(
        responses.GET,
        BASE_URL,
        match=[
            responses.matchers.query_param_matcher(
                {"query": "AUTHOR-NAME(Albert)", "count": "10", "apiKey": api_key}
            )
        ],
        body=mock_Elsevier_response(
            [
                {
                    "prism:doi": "doi1",
                    "dc:title": "Sample Paper 1",
                    "prism:coverDate": "2024-01-01",
                    "prism:publicationName": "Sample Journal",
                    "subtypeDescription": "Research Article",
                    "author": [{"authname": "Albert"}],  
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
                {"query": "AUTHOR-NAME(Joe)", "count": "10", "apiKey": api_key}
            )
        ],
        body=mock_Elsevier_response(
            [
                {
                    "prism:doi": "doi1",
                    "dc:title": "Sample Paper 1",
                    "prism:coverDate": "2024-01-01",
                    "prism:publicationName": "Sample Journal",
                    "subtypeDescription": "Research Article",
                    "author": [{"authname": "Joe"}],                   
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
                {"query": "AUTHOR-NAME(Allen)", "count": "10", "apiKey": api_key}
            )
        ],
        body=mock_Elsevier_response(
            [
                {
                    "prism:doi": "doi1",
                    "dc:title": "Sample Paper",
                    "prism:coverDate": "2024-01-01",
                    "prism:publicationName": "Sample Journal",
                    "subtypeDescription": "Research Article",
                    "author": [{"authname": "Allen"}],
                }
            ]
        ),
        status=200,
    )

    results = Elsevier.search_multiple_authors(["Albert", "Joe", "Allen"])
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
                {
                    "query": "AUTHOR-NAME(Magert O. Adekunle)",
                    "count": "10",
                    "apiKey": api_key,
                }
            )
        ],
        body=mock_Elsevier_response([]),
        status=200,
    )

    results = Elsevier.search_multiple_authors(["Magert O. Adekunle"])
    assert results.get("Magert O. Adekunle") == []


def test_limit_number_of_results(mock_api):
    """Test limiting the number of results using `rows`."""
    mock_api.add(
        responses.GET,
        BASE_URL,
        match=[
            responses.matchers.query_param_matcher(
                {
                    "query": "AUTHOR-NAME(Timothy C. Moore)",
                    "count": "2",
                    "apiKey": api_key,
                }
            )
        ],
        body=json.dumps(
            {
                "search-results": {
                    "entry": [
                        {
                            "prism:doi": "doi1",
                            "dc:title": "Sample Paper 1",
                            "prism:coverDate": "2024-01-01",
                            "prism:publicationName": "Sample Journal",
                            "subtypeDescription": "Research Article",
                            "author": [{"authname": "Timothy C. Moore"}],
                        },
                        {
                            "prism:doi": "doi2",
                            "dc:title": "Sample Paper 2",
                            "prism:coverDate": "2024-01-01",
                            "prism:publicationName": "Sample Journal",
                            "subtypeDescription": "Research Article",
                            "author": [{"authname": "Timothy C. Moore"}],
                        },
                    ]
                }
            }
        ),
        status=200,
    )

    results = Elsevier.search_multiple_authors(["Timothy C. Moore"], limit=2)
    assert len(results["Timothy C. Moore"]) == 2
    assert results["Timothy C. Moore"][0]["title"] == "Sample Paper 1"
    assert results["Timothy C. Moore"][1]["title"] == "Sample Paper 2"


def test_initials_lastname(mock_api):
    """Test searching with initials and last name finds a specific paper."""
    mock_api.add(
        responses.GET,
        BASE_URL,
        match=[
            responses.matchers.query_param_matcher(
                {
                    "query": "AUTHOR-NAME(Randy J. Nelson)",
                    "count": "10",
                    "apiKey": api_key,
                }
            )
        ],
        body=json.dumps(
            {
                "search-results": {
                    "entry": [
                        {
                            "prism:doi": "doi1",
                            "dc:title": "Disrupted Circadian Rhythms and Substance Use Disorders: A Narrative Review",
                            "prism:coverDate": "2024-01-01",
                            "prism:publicationName": "Sample Journal",
                            "subtypeDescription": "Research Article",
                            "author": [{"authname": "Randy J. Nelson"}],
                        },
                    ]
                }
            }
        ),
        status=200,
    )
    results = Elsevier.search_multiple_authors(["Randy J. Nelson"])
    assert len(results["Randy J. Nelson"]) > 0
    assert (results["Randy J. Nelson"][0]["title"] == "Disrupted Circadian Rhythms and Substance Use Disorders: A Narrative Review")
