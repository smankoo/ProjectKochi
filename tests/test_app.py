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

def test_download(client):
    response = client.post('/', data={'url':'https://www.youtube.com/watch?v=P5joP3Ba4cQ'})
    assert response is not None
    assert response.status_code == 200
    assert response.content_type == 'audio/mpeg'
    assert response.content_length == 3130657
    return(response)

if __name__ == '__main__':
    app = create_app()
    client = app.test_client()
    r = test_download(client)
    print('Done')

    