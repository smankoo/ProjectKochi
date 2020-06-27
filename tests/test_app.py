import os
import tempfile

import pytest

from kochi import create_app

@pytest.fixture
def app():
    app = create_app()
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


def test_index(client):
    response = client.get('/')
    assert b'<input' in response.data
    assert b'type="submit"' in response.data