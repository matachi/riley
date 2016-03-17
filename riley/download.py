import cgi
import os
import time
from functools import partial
from urllib.parse import urlparse

import requests
from clint.textui.progress import Bar


def download(url, to_dir, datetime=None):
    """
    :type url: str
    :type to_dir: str
    :type datetime: time.struct_time
    """
    os.makedirs(to_dir, exist_ok=True)
    response = requests.get(url, stream=True)
    save_path = os.path.join(to_dir, get_file_name(response))
    with open(save_path, 'wb') as f:
        content_length = response.headers.get('content-length')
        if content_length is None:
            download = partial(_download, response)
        else:
            length = int(content_length)
            download = partial(_download_with_progressbar, response, length)
        for block in download():
            f.write(block)
    if datetime is not None:
        unix_timestamp = int(time.mktime(datetime))
        os.utime(save_path, (unix_timestamp, unix_timestamp))


def _download(response):
    """
    :type response: requests.Response
    """
    for i, block in enumerate(response.iter_content(1024), 1):
        yield block


def _download_with_progressbar(response, content_length):
    """
    :type response: requests.Response
    :type content_length: int
    """
    with Bar(expected_size=content_length) as bar:
        for i, block in enumerate(response.iter_content(1024), 1):
            yield block
            bar.show(min(i * 1024, content_length))


def get_file_name(response):
    """
    :type response: requests.Response
    :rtype: str
    """
    if 'Content-Disposition' in response.headers:
        _value, params = cgi.parse_header(
            response.headers['Content-Disposition'])
        return params['filename']
    # Delete query junk from end of the the URL
    path = urlparse(response.url)[2]
    # Only keep the name
    filename = os.path.basename(path)
    return filename
