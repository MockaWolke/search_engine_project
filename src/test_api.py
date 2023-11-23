import pytest
from .myapi import app
from flask import url_for


@pytest.fixture
def client():
    app.config["SERVER_NAME"] = "localhost"
    with app.app_context():
        with app.test_client() as client:
            yield client


def test_start_page(client):
    """Test the start page"""
    url = url_for(
        "start"
    )  # Assuming 'start' is the view function name for the start page
    response = client.get(url)
    assert response.status_code == 200
    response_text = response.data.decode("utf-8")
    assert "Welcome to Our Search Engine" in response_text
    assert "Search within the" in response_text


def test_query_index(client):
    """Test the /query route with various scenarios"""

    # Test for a valid query
    url = url_for("query_index", q="food", p=1)
    response = client.get(url)
    assert response.status_code == 200
    # Add more assertions as needed

    # Test for a very high page number (pagination edge case)
    url = url_for("query_index", q="example query", p=100000)
    response = client.get(url)
    assert response.status_code == 200
    # Add more assertions as needed

    # Test for an empty query string
    url = url_for("query_index", q="", p=1)
    response = client.get(url)
    assert response.status_code == 200  # or another appropriate status code
    response_text = response.data.decode("utf-8")
    assert "Something Went Wrong" in response_text

    # Test for a non-integer page number
    url = url_for("query_index", q="example query", p="abc")
    response = client.get(url)
    assert response.status_code == 200  # or another appropriate status code
    response_text = response.data.decode("utf-8")
    assert "Something Went Wrong" in response_text

    # Test for a negative page number
    url = url_for("query_index", q="example query", p=-1)
    response = client.get(url)
    assert response.status_code == 200  # or another appropriate status code
    response_text = response.data.decode("utf-8")
    assert "Something Went Wrong" in response_text
    # Add more assertions as needed
