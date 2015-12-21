import cgi
import os
from urllib.parse import urlparse

from clint.textui.progress import Bar
import requests


def download(url, to_dir):
    response = requests.get(url, stream=True)
    save_path = os.path.join(to_dir, get_file_name(response))
    with open(save_path, 'wb') as f:
        total_length = int(response.headers.get('content-length'))
        with Bar(expected_size=total_length) as bar:
            for i, block in enumerate(response.iter_content(1024), 1):
                f.write(block)
                bar.show(min(i * 1024, total_length))


def get_file_name(response):
    if 'Content-Disposition' in response.headers:
        _value, params = cgi.parse_header(
            response.headers['Content-Disposition'])
        return params['filename']
    # Delete query junk from end of the the URL
    path = urlparse(response.url)[2]
    # Only keep the name
    filename = os.path.basename(path)
    return filename
