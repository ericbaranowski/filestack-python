import json
import mimetypes
import os.path
import pytest
import requests
import responses

from filestack import Client, Filelink
from filestack.config import MULTIPART_START_URL, MULTIPART_UPLOAD_URL, MULTIPART_COMPLETE_URL
from filestack.utils import upload_utils

APIKEY = 'APIKEY'
HANDLE = 'SOMEHANDLE'
URL = "https://cdn.filestackcontent.com/{}".format(HANDLE)


@pytest.fixture
def client():
    return Client(APIKEY)


@responses.activate
def test_upload_multipart(monkeypatch, client):
    def mock_filename(path):
        return [None, 'notbird.jpg']
    def mock_filesize(path):
        return 10 * 1024 ** 2
    def mock_mimetype(path):
        return [None, 'image/jpeg']

    monkeypatch.setattr(os.path, 'split', mock_filename)
    monkeypatch.setattr(os.path, 'getsize', mock_filesize)
    monkeypatch.setattr(mimetypes, 'guess_type', mock_mimetype)

    responses.add(responses.POST, MULTIPART_START_URL, status=200, content_type="application/json",
                  json={"region": "us-east-1", "upload_id": "someuuid", "uri": "someuri", "location_url": "somelocation"})

    responses.add(responses.POST, MULTIPART_UPLOAD_URL, status=200, content_type="application/json", json={'url': URL, "headers": {}})

    def chunk_put_callback(request):
        body = {'url': URL}
        return (200, {'ETag': 'someetags'}, json.dumps(body))

    responses.add_callback(responses.PUT, URL, callback=chunk_put_callback)

    responses.add(responses.POST, MULTIPART_COMPLETE_URL, status=200, content_type="application/json", json={"url": URL})
    new_filelink = client.upload(filepath='bird.jpg')

    assert new_filelink.handle == HANDLE

