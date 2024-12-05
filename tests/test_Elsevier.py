import pytest
import responses
import logging

from pubscraper.APIClasses import Elsevier

logging.basicConfig(level=logging.DEBUG)

BASE_URL = "https://api.elsevier.com/content/search/scopus"

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


# def test_no_input(mock_api):
#     """Test that providing no input returns an empty result."""
#     results = Elsevier.search_multiple_authors([])
#     assert results == {}
#     assert len(mock_api.calls) == 0  # No requests should have been made


# def test_partial_empty_input(mock_api):
#     """Test handling of partial empty input in author list."""

#     # Mock response for "albert"
#     mock_api.add(
#         responses.GET,
#         BASE_URL,
#         match=[
#             responses.matchers.query_param_matcher(
#                 {"query": 'AUTHOR-NAME(Albert)', "count": "10", "apiKey": "mock_api_key"}
#             )
#         ],
#         body=mock_Elsevier_response(
#             [
#                 {
#                     "title": "Sample Paper",
#                     "author": [{"name": "Albert"}],
#                     "published": "2024-01-01",
#                 }
#             ]
#         ),
#         status=200,
#     )
#     results = Elsevier.search_multiple_authors(["Albert", ""])

#     assert len(results) == 1
#     assert "Albert" in results
#     assert len(mock_api.calls) == 1


# def test_search_all_names(mock_api):
#     mock_api.add(
#         responses.GET,
#         BASE_URL,
#         match=[
#             responses.matchers.query_param_matcher(
#                 {"query": 'AUTHOR-NAME(Albert)', "count": "10", "apiKey": "mock_api_key"}
#             )
#         ],
#         body=mock_Elsevier_response(
#             [
#                 {
#                     "title": "Sample Paper",
#                     "author": [{"name": "Albert"}],
#                     "published": "2024-01-01",
#                 }
#             ]
#         ),
#         status=200,
#     )
#     mock_api.add(
#         responses.GET,
#         BASE_URL,
#         match=[
#             responses.matchers.query_param_matcher(
#                 {"query": 'AUTHOR-NAME(Joe)', "count": "10", "apiKey": "mock_api_key"}
#             )
#         ],
#         body=mock_Elsevier_response(
#             [
#                 {
#                     "title": "Sample Paper",
#                     "author": [{"name": "Joe"}],
#                     "published": "2024-01-01",
#                 }
#             ]
#         ),
#         status=200,
#     )
#     mock_api.add(
#         responses.GET,
#         BASE_URL,
#         match=[
#             responses.matchers.query_param_matcher(
#                 {"query": 'AUTHOR-NAME(Allen)', "count": "10", "apiKey": "mock_api_key"}
#             )
#         ],
#         body=mock_Elsevier_response(
#             [
#                 {
#                     "title": "Sample Paper",
#                     "author": [{"name": "Allen"}],
#                     "published": "2024-01-01",
#                 }
#             ]
#         ),
#         status=200,
#     )

#     results = Elsevier.search_multiple_authors(["Albert", "Joe", "Allen"])
#     assert len(results) == 3
#     assert "Albert" in results
#     assert "Joe" in results
#     assert "Allen" in results


# def test_no_results_for_name(mock_api):
#     """Test that an author with no results returns None."""
#     mock_api.add(
#         responses.GET,
#         BASE_URL,
#         match=[
#             responses.matchers.query_param_matcher(
#                 {"query": 'AUTHOR-NAME(Magert O. Adekunle)', "count": "10", "apiKey": "mock_api_key"}
#             )
#         ],
#         body=mock_Elsevier_response([]),
#         status=200,
#     )

#     results = Elsevier.search_multiple_authors(["Magert O. Adekunle"])
#     assert results.get("Magert O. Adekunle") == []


# def test_limit_number_of_results(mock_api):
#     """Test limiting the number of results using `rows`."""
#     mock_api.add(
#         responses.GET,
#         BASE_URL,
#         match=[
#             responses.matchers.query_param_matcher(
#                 {"query": 'AUTHOR-NAME(Timothy C. Moore)', "count": "2", "apiKey": "mock_api_key"}
#             )
#         ],
#         body=json.dumps({
#             "response": {
#                 "docs": [
#                     {
#                         "id": "doi1",
#                         "title_display": "Sample Paper 1",
#                         "author_display": ["Allen"],
#                         "publication_date": "2024-01-01",
#                         "journal": "Sample Journal",
#                         "article_type": "Research Article"
#                     },
#                     {
#                         "id": "doi2",
#                         "title_display": "Sample Paper 2",
#                         "author_display": ["Allen"],
#                         "publication_date": "2024-01-01",
#                         "journal": "Sample Journal",
#                         "article_type": "Research Article"
#                     }
#                 ]
#             }
#         }),
#         status=200,
#         content_type="application/json"
#     )
    
#     results = Elsevier.search_multiple_authors(["Timothy C. Moore"], limit=2)
#     assert len(results["Timothy C. Moore"]) == 2



# def test_initials_lastname():
#     """Test searching with initials and last name finds a specific paper."""
#     results = Elsevier.search_multiple_authors(["Randy J. nelson"])
#     publications_found = results["Randy J. nelson"]
#     assert any("Disrupted Circadian Rhythms and Substance Use Disorders: A Narrative Review" in pub["title"] for pub in publications_found)


# def test_fullname():
#     """Test searching with full name finds a specific paper."""
#     results = Elsevier.search_multiple_authors(["Randy Nelson"])
#     publications_found = results["Randy Nelson"]
#     assert any("Disrupted Circadian Rhythms and Substance Use Disorders: A Narrative Review" in pub["title"] for pub in publications_found)


# def test_result_parity():
#     """Test that results are the same when searching with full name or initials."""
#     results_one = Elsevier.search_multiple_authors(["Randy J. Nelson"])
#     results_two = Elsevier.search_multiple_authors(["Randy J. Nelson"])
#     results_three = Elsevier.search_multiple_authors(["Randy Nelson"])
#     assert (
#         results_one["Randy J. Nelson"] == results_two["Randy J. Nelson"] == results_three["Randy Nelson"]
#     )



# def test_single_author_query(mock_api):
#     """Test querying a single author and getting expected results."""
    
#     # Mock response for "Jane Doe"
#     mock_api.add(
#         responses.GET,
#         BASE_URL,
#         match=[
#             responses.matchers.query_param_matcher(
#                 {"query": 'author:"Jane Doe"', "count": "10", "apiKey": "mock_api_key"}
#             )
#         ],
#         body=json.dumps(
#             mock_Elsevier_response(
#                 [
#                     {
#                         "title": "Research on AI",
#                         "author": [{"name": "Jane Doe"}],
#                         "published": "2023-12-01",
#                         "journal": "AI Research Journal",
#                     }
#                 ]
#             )
#         ),
#         status=200,
#         content_type="application/json",
#     )

#     # Call the function
#     results = Elsevier.search_multiple_authors(["Jane Doe"])

#     # Assertions
#     assert len(results) == 1  # One author
#     assert "Jane Doe" in results  # Key matches the queried author
#     assert len(results["Jane Doe"]) == 1  # One result for the author
#     assert results["Jane Doe"][0]["title"] == "Research on AI"  # Verify result details
#     assert results["Jane Doe"][0]["journal"] == "AI Research Journal"  # Verify journal
