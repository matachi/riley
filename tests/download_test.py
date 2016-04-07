import os
import time
from unittest.mock import MagicMock
from riley.download import get_file_name, download


def test_get_file_name_from_header():
    # Example of a feed with such files: http://feeds.podtrac.com/fNBYjm-45_h8
    response = MagicMock()
    response.headers = {
        'Content-Disposition': 'attachment;filename="2015-11-10.mp3"'}
    assert get_file_name(response) == '2015-11-10.mp3'


def test_get_file_name_when_content_disposition_filename_is_missing():
    # Example of a feed with such files:
    # http://feeds.wnyc.org/radiolab?format=xml
    response = MagicMock()
    response.headers = {'Content-Disposition': 'attachment'}
    response.url = 'http://feeds.wnyc.org/~r/radiolab/~5/KYQG_JtkTYM/radiolab_podcast16cellmates.mp3'
    assert get_file_name(response) == 'radiolab_podcast16cellmates.mp3'


def test_get_file_name_from_url():
    # The filename is not among the headers, here is a feed fith such examples:
    # http://tackforkaffet.libsyn.com/rss
    response = MagicMock()
    response.url = 'http://traffic.libsyn.com/tackforkaffet/TFK.246_-_1999.mp3'
    assert get_file_name(response) == 'TFK.246_-_1999.mp3'


def test_get_file_name_from_redirected_url():
    # The URL in the test above does in fact redirect to something with a lot
    # of junk at the end.
    response = MagicMock()
    response.url = 'http://hwcdn.libsyn.com/p/9/5/4/954c927f0cde7060/TFK.246_-_1999.mp3?c_id=10199983&expiration=1447188914&hwt=e02ddd7a1b52bb9104bdcd864a5ace36'
    assert get_file_name(response) == 'TFK.246_-_1999.mp3'


def test_prefer_name_from_headers():
    response = MagicMock()
    response.headers = {}
    response.url = 'http://example.com/abc.mp3'
    assert get_file_name(response) == 'abc.mp3'
    response.headers = {'Content-Disposition': 'attachment;filename="def.mp3"'}
    assert get_file_name(response) == 'def.mp3'


def dummy_download(*args):
    for b in [b'a', b'b', b'c']:
        yield b


def test_download_url(tmpdir, monkeypatch):
    monkeypatch.setattr('riley.download._download', dummy_download)

    response = MagicMock()
    response.url = 'http://example.com/123.mp3'
    response.headers.get.return_value = None
    # The header 'content-length' is missing, which was the case with
    # http://www.linuxvoice.com/podcast_opus.rss
    monkeypatch.setattr(
        'riley.download.requests.get', lambda x, stream: response)

    time_struct = time.strptime('2015-11-12 01:02:03', '%Y-%m-%d %H:%M:%S')

    download(response.url, tmpdir.strpath, time_struct)

    file = tmpdir.join('123.mp3')
    assert file.read() == 'abc'
    assert os.stat(file.strpath).st_mtime == time.mktime(time_struct)
