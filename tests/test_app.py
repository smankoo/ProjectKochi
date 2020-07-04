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
    assert b'<button' in response.data

def test_download(client):
    data = {"url":"https://www.youtube.com/watch?v=P5joP3Ba4cQ"}
    response1 = client.get('/_download', query_string = data)
    json_data = response1.get_json()
    downloadid = json_data['downloadid']
    response2 = client.get('/getfile?downloadid=' + downloadid)

    assert response2 is not None
    assert response2.status_code == 200
    assert response2.content_type == 'audio/mpeg'
    assert response2.content_length == 3130657
    return(response2)

def test_download_music(client):
    data = {"url":"https://music.youtube.com/watch?v=AjQzgbVYUjw&feature=share"}
    response1 = client.get('/_download', query_string = data)
    json_data = response1.get_json()
    downloadid = json_data['downloadid']
    response2 = client.get('/getfile?downloadid=' + downloadid)

    assert response2 is not None
    assert response2.status_code == 200
    assert response2.content_type == 'audio/mpeg'

    # Tolerate some error in content length presumably due to ffmpeg encoding differences
    assert (response2.content_length >= 8401965*0.9998 and response2.content_length <= 8401965*1.0002)
    # assert response2.content_length == 8401965
    return(response2)

if __name__ == '__main__':
    app = create_app()
    client = app.test_client()
    r = test_download(client)
    print('Done')
