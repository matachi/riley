import cgi
import os
from urllib.parse import urlparse
import requests


def download(url, to_dir):
    response = requests.get(url, stream=True)
    save_path = os.path.join(to_dir, get_file_name(response))
    with open(save_path, 'wb') as f:
        for block in response.iter_content(1024):
            f.write(block)


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
