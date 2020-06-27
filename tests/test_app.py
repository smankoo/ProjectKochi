import os
import tempfile

import pytest

import app

@pytest.fixture
def client():
    # db_fd, flaskr.app.config['DATABASE'] = tempfile.mkstemp()
    app.config['TESTING'] = True

    with app.test_client() as client:
        # with flaskr.app.app_context():
        #     flaskr.init_db()
        yield client

    # os.close(db_fd)
    # os.unlink(flaskr.app.config['DATABASE'])

def test_download():
    response = client.get('/')
    assert b'<input' in response.data
    assert b'type="submit"' in response.data