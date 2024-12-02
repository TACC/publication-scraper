import pytest
import responses
from pubscraper.APIClasses import arXiv
import logging

logging.basicConfig(level=logging.DEBUG)

BASE_URL = "http://export.arxiv.org/api/query"


@pytest.fixture
def mock_api():
    with responses.RequestsMock() as rsps:
        yield rsps


def mock_arxiv_response(entries):
    """Helper function to generate mock XML response."""
    return f"""
    <feed xmlns="http://www.w3.org/2005/Atom">
        {"".join(entries)}
    </feed>
    """

def test_skip_empty_name(mock_api):
    """Test skipping empty author names."""
    results = arXiv.search_multiple_authors([""])

    assert results == {}
    assert len(mock_api.calls) == 0  # No requests should have been made


def test_no_input(mock_api):
    """Test that providing no input returns an empty result."""
    results = arXiv.search_multiple_authors([])
    assert results == {}
    assert len(mock_api.calls) == 0  # No requests should have been made


def test_partial_empty_input(mock_api):
    """Test handling of partial empty input in author list."""
    
    # Mock response for "albert"
    mock_api.add(
        responses.GET,
        BASE_URL,
        match=[
            responses.matchers.query_param_matcher({
                "search_query": 'au:"Albert"',
                "start": "0",
                "max_results": "10"
            })
        ],
        body=mock_arxiv_response([
            """<entry>
                <title>Sample Paper</title>
                <author><name>Albert</name></author>
                <published>2024-01-01</published>
            </entry>"""
        ]),
        status=200,
    )
    results = arXiv.search_multiple_authors(["Albert", ""])
    
    assert len(results) == 1 
    assert "Albert" in results
    assert len(mock_api.calls) == 1 


def test_search_all_names(mock_api):
    mock_api.add(
        responses.GET,
        BASE_URL,
        match=[
            responses.matchers.query_param_matcher({
                "search_query": 'au:"Albert"',
                "start": "0",
                "max_results": "10"
            })
        ],
        body=mock_arxiv_response([
            """<entry>
                <title>Paper 1</title>
                <author><name>Albert</name></author>
                <published>2024-01-01</published>
            </entry>"""
        ]),
        status=200,
    )
    mock_api.add(
        responses.GET,
        BASE_URL,
        match=[
            responses.matchers.query_param_matcher({
                "search_query": 'au:"Joe"',
                "start": "0",
                "max_results": "10"
            })
        ],
        body=mock_arxiv_response([
            """<entry>
                <title>Paper 2</title>
                <author><name>Joe</name></author>
                <published>2024-02-01</published>
            </entry>"""
        ]),
        status=200,
    )
    mock_api.add(
        responses.GET,
        BASE_URL,
        match=[
            responses.matchers.query_param_matcher({
                "search_query": 'au:"Allen"',
                "start": "0",
                "max_results": "10"
            })
        ],
        body=mock_arxiv_response([
            """<entry>
                <title>Paper 3</title>
                <author><name>Allen</name></author>
                <published>2024-03-01</published>
            </entry>"""
        ]),
        status=200,
    )

    results = arXiv.search_multiple_authors(["Albert", "Joe", "Allen"])
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
            responses.matchers.query_param_matcher({
                "search_query": 'au:"Magert O. Adekunle"',
                "start": "0",
                "max_results": "10"
            })
        ],
        body=mock_arxiv_response([]), 
        status=200,
    )

    results = arXiv.search_multiple_authors(["Magert O. Adekunle"])
    assert results.get("Magert O. Adekunle") == []


def test_limit_number_of_results(mock_api):
    """Test limiting the number of results using `max_results`."""
    mock_api.add(
        responses.GET,
        BASE_URL,
        match=[
            responses.matchers.query_param_matcher({
                "search_query": 'au:"Timothy C. Moore"',
                "start": "0",
                "max_results": "2"
            })
        ],
        body=mock_arxiv_response([
            """<entry>
                <title>Paper 1</title>
                <author><name>Timothy C. Moore</name></author>
                <published>2024-01-01</published>
            </entry>""",
            """<entry>
                <title>Paper 2</title>
                <author><name>Timothy C. Moore</name></author>
                <published>2024-02-01</published>
            </entry>"""
        ]),
        status=200,
    )

    results = arXiv.search_multiple_authors(["Timothy C. Moore"], max_results=2)
    assert len(results["Timothy C. Moore"]) == 2