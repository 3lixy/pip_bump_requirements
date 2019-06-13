import requests


class PyPiApi(object):
    # https://warehouse.readthedocs.io/api-reference/json/
    base_url = "https://pypi.python.org/pypi"

    def _get(self, path):
        url = f'{self.base_url.rstrip("/")}/{path.lstrip("/")}/json'
        r = requests.get(url)
        r.raise_for_status()
        return r.json()

    def project(self, project):
        return self._get(project)

    def project_release(self, project, release):
        return self._get(f'{project}/{release}')
