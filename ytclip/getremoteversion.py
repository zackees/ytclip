"""Get the version of the module from PyPI."""

from typing import Optional

import requests  # type: ignore

URL = "https://pypi.org/pypi/ytclip/json"
TIMEOUT = 10


def get_remote_version() -> Optional[str]:
    """Returns the version of the module."""
    try:
        response = requests.get(URL, timeout=TIMEOUT)
    except requests.exceptions.RequestException:
        return None
    if response.status_code != 200:
        return None
    try:
        return response.json()["info"]["version"]
    except KeyError:
        return None


if __name__ == "__main__":
    print(get_remote_version())
