from unittest.mock import MagicMock
from riley.download import get_file_name


def test_get_file_name_from_header():
    # Example of a feed with such files: http://feeds.podtrac.com/fNBYjm-45_h8
    response = MagicMock()
    response.headers = {
        'Content-Disposition': 'attachment;filename="2015-11-10.mp3"'}
    assert get_file_name(response) == '2015-11-10.mp3'


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
