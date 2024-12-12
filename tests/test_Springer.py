import pytest
import responses

from pubscraper.APIClasses import Springer


@pytest.fixture
def test_skip_empty_name():
    """Test that providing an empty author name returns an empty result."""
    results = Springer.search_multiple_authors([""])
    assert results == {}


def test_no_input():
    """Test that providing no input returns an empty result."""
    results = Springer.search_multiple_authors([])
    assert results == {}


@responses.activate
def test_partial_empty_input():
    """Test that if one author is empty, it skips that author."""
    response_1 = responses.Response(
        method="GET",
        url="https://api.springernature.com/openaccess/json",
        status=200,
        json={
            "records": [
                {
                    "title": "some title",
                    "publicationName": "albert",
                    "publicationDate": "2000-09-06",
                    "contentType": "journal",
                    "doi": "some doi",
                }
            ]
        },
    )
    responses.add(response_1)

    results = Springer.search_multiple_authors(["albert", ""])
    assert len(results) == 1


@responses.activate
def test_search_all_names():
    """Test searching for multiple author names returns expected number of results."""
    response_1 = responses.Response(
        method="GET",
        url="https://api.springernature.com/openaccess/json",
        status=200,
        json={
            "records": [
                {
                    "title": "some title",
                    "publicationName": "publication name",
                    "publicationDate": "2000-09-06",
                    "contentType": "journal",
                    "doi": "some doi",
                    "creators": [{"creator": "albert"}],
                }
            ]
        },
    )
    responses.add(response_1)
    response_2 = responses.Response(
        method="GET",
        url="https://api.springernature.com/openaccess/json",
        status=200,
        json={
            "records": [
                {
                    "title": "some title",
                    "publicationName": "publication name",
                    "publicationDate": "2000-09-06",
                    "contentType": "journal",
                    "doi": "some doi",
                    "creators": [{"creator": "joe"}],
                }
            ]
        },
    )
    responses.add(response_2)
    response_3 = responses.Response(
        method="GET",
        url="https://api.springernature.com/openaccess/json",
        status=200,
        json={
            "records": [
                {
                    "title": "some title",
                    "publicationName": "publication name",
                    "publicationDate": "2000-09-06",
                    "contentType": "journal",
                    "doi": "some doi",
                    "creators": [{"creator": "allen"}],
                }
            ]
        },
    )
    responses.add(response_3)
    results = Springer.search_multiple_authors(["albert", "joe", "allen"])
    assert len(results) == 3


@responses.activate
def test_no_results():
    response_1 = responses.Response(
        method="GET",
        url="https://api.springernature.com/openaccess/json",
        status=200,
        json={"records": []},
    )
    responses.add(response_1)
    """Test that a name with no results returns an empty list for that name."""
    results = Springer.search_multiple_authors(["Magret O Adekunle"])
    assert results == {"Magret O Adekunle": []}


@responses.activate
def test_initials_lastname():
    response_1 = responses.Response(
        method="GET",
        url="https://api.springernature.com/openaccess/json",
        status=200,
        json={
            "records": [
                {
                    "title": "Historical Social Network Analysis and Early Financial Exchanges",
                    "publicationName": "publication name",
                    "publicationDate": "2000-09-06",
                    "contentType": "journal",
                    "doi": "some doi",
                    "creators": [{"creator": "Timothy C Moore"}],
                }
            ]
        },
    )
    responses.add(response_1)
    """Test searching with initials and last name finds a specific paper."""
    results = Springer.search_multiple_authors(["Timothy C Moore"])
    publications_found = results["Timothy C Moore"]
    assert any(
        "Historical Social Network Analysis and Early Financial Exchanges"
        in pub["title"]
        for pub in publications_found
    )


@responses.activate
def test_fullname():
    response_1 = responses.Response(
        method="GET",
        url="https://api.springernature.com/openaccess/json",
        status=200,
        json={
            "records": [
                {
                    "title": "Historical Social Network Analysis and Early Financial Exchanges",
                    "publicationName": "publication name",
                    "publicationDate": "2000-09-06",
                    "contentType": "journal",
                    "doi": "some doi",
                    "creators": [{"creator": "Timothy C. Moore"}],
                }
            ]
        },
    )
    responses.add(response_1)
    """Test searching with full name finds a specific paper."""
    results = Springer.search_multiple_authors(["Timothy C. Moore"])
    publications_found = results["Timothy C. Moore"]
    assert any(
        "Historical Social Network Analysis and Early Financial Exchanges"
        in pub["title"]
        for pub in publications_found
    )


@responses.activate
def test_limit_number_of_results():
    response_1 = responses.Response(
        method="GET",
        url="https://api.springernature.com/openaccess/json",
        status=200,
        json={
            "records": [
                {
                    "title": "Historical Social Network Analysis and Early Financial Exchanges",
                    "publicationName": "publication name",
                    "publicationDate": "2000-09-06",
                    "contentType": "journal",
                    "doi": "some doi",
                    "creators": [{"creator": "Timothy C Moore"}],
                },
                {
                    "title": "Another Title",
                    "publicationName": "publication name",
                    "publicationDate": "2000-09-06",
                    "contentType": "journal",
                    "doi": "some doi",
                    "creators": [{"creator": "Timothy C Moore"}],
                },
            ]
        },
    )
    responses.add(response_1)

    """Test that the number of results is limited when specified."""
    results = Springer.search_multiple_authors(["Timothy C Moore"], limit=2)
    assert len(results["Timothy C Moore"]) == 2
