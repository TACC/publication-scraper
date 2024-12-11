import pytest
import responses

from pubscraper.APIClasses import MDPI
import pubscraper.config as config

BASE_URL = config.MDPI_URL


@pytest.fixture
def mock_api():
    with responses.RequestsMock() as rsps:
        yield rsps


def mock_MDPI_response(entries):
    """Helper function to generate mock JSON response."""
    return {"feed": {"entries": entries}}


def test_skip_empty_name(mock_api):
    """Test skipping empty author names."""
    results = MDPI.search_multiple_authors([""])
    assert results == {}
    assert len(mock_api.calls) == 0  # No requests should have been made


def test_no_input(mock_api):
    """Test that providing no input returns an empty result."""
    results = MDPI.search_multiple_authors([])
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
                {
                    "query.author": "Albert",
                    "rows": "10",
                    "offset": 0,
                    "mailto": "ma57489@my.utexas.edu",
                }
            )
        ],
        body=mock_MDPI_response(
            {
                "message": {
                    "items": [
                        {
                            "title": "Sample Paper",
                            "author": [{"name": "Albert"}],
                            "published": "2024-01-01",
                            "DOI": "10.1234/sample.doi"
                        }
                    ],
                    "total-results": 1
                }
            }
        ),
        status=200,
    )
    results = MDPI.search_multiple_authors(["Albert", ""])
    assert len(results) == 1
    assert "Albert" in results
    assert len(mock_api.calls) == 1


def test_search_all_names(mock_api):
    """Test handling of mutiple entries in the auhtor list."""
    mock_api.add(
        responses.GET,
        BASE_URL,
        match=[
            responses.matchers.query_param_matcher(
                {
                    "query.author": "Albert",
                    "rows": "10",
                    "offset": 0,
                    "mailto": "ma57489@my.utexas.edu",
                }
            )
        ],
        body=mock_MDPI_response(
            {
                "message": {
                    "items": [
                        {
                            "title": "Sample Paper",
                            "author": [{"name": "Albert"}],
                            "published": "2024-01-01",
                            "DOI": "10.1234/sample.doi"
                        }
                    ],
                    "total-results": 1
                }
            }
        ),
        status=200,
    )
    mock_api.add(
        responses.GET,
        BASE_URL,
        match=[
            responses.matchers.query_param_matcher(
                {
                    "query.author": "Joe",
                    "rows": "10",
                    "offset": 0,
                    "mailto": "ma57489@my.utexas.edu",
                }
            )
        ],
        body=mock_MDPI_response(
            {
                "message": {
                    "items": [
                        {
                            "title": "Sample Paper",
                            "author": [{"name": "Joe"}],
                            "published": "2024-01-01",
                            "DOI": "10.1234/sample.doi"
                        }
                    ],
                    "total-results": 1
                }
            }
        ),
        status=200,
    )
    mock_api.add(
        responses.GET,
        BASE_URL,
        match=[
            responses.matchers.query_param_matcher(
                {
                    "query.author": "Allen",
                    "rows": "10",
                    "offset": 0,
                    "mailto": "ma57489@my.utexas.edu",
                }
            )
        ],
        body=mock_MDPI_response(
            {
                "message": {
                    "items": [
                        {
                            "title": "Sample Paper",
                            "author": [{"name": "Allen"}],
                            "published": "2024-01-01",
                            "DOI": "10.1234/sample.doi"
                        }
                    ],
                    "total-results": 1
                }
            }
        ),
        status=200,
    )
    results = MDPI.search_multiple_authors(["Albert", "Joe", "Allen"])
    assert len(results) == 3
    assert "Albert" in results
    assert "Joe" in results
    assert "Allen" in results


def test_no_results(mock_api):
    """Test that an author with no results returns None."""
    mock_api.add(
        responses.GET,
        BASE_URL,
        match=[
            responses.matchers.query_param_matcher(
                {
                    "query.author": "Magert+O.+Adekunle",
                    "rows": "10",
                    "offset": 0,
                    "mailto": "ma57489@my.utexas.edu",
                }
            )
        ],
        body=mock_MDPI_response(
            {
                "message": {
                    "items": [
                        {
                            "title": "Sample Paper",
                            "author": [{"name": "Magert O. Adekunle"}],
                            "published": "2024-01-01",
                            "DOI": "10.1234/sample.doi"
                        }
                    ],
                    "total-results": 1
                }
            }
        ),
        status=200,
    ) 
    results = MDPI.search_multiple_authors(["Magert O. Adekunle"])
    assert results.get("Magert O. Adekunle") == []


def test_limit_results(mock_api):
    """Test limiting the number of results using `rows`."""
    mock_api.add(
        responses.GET,
        BASE_URL,
        match=[
            responses.matchers.query_param_matcher(
                {
                    "query.author": "Allen",
                    "rows": "2",
                    "offset": 0,
                    "mailto": "ma57489@my.utexas.edu",
                }
            )
        ],
        body=mock_MDPI_response(
            {
                "message": {
                    "items": [
                        {
                            "title": "Sample Paper",
                            "author": [{"name": "Allen"}],
                            "published": "2024-01-01",
                            "DOI": "10.1234/sample.doi"
                        },
                        {
                            "title": "Sample Paper",
                            "author": [{"name": "Allen"}],
                            "published": "2024-01-01",
                            "DOI": "10.1234/sample.doi"
                        },
                    ],
                    "total-results": 2
                }
            }
        ),
        status=200,
    )  
    results = MDPI.search_multiple_authors(["Allen"], rows=2)
    assert len(results["Allen"]) < 10