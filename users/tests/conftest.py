import os
import sys
import tempfile
import json

from dulwich.repo import Repo
from dulwich.errors import NotGitRepository
import dulwich.porcelain as git

import pytest
import rdamsc_userctl


class App(object):
    def __init__(self, path):
        self.path = os.path.join(path, 'users', 'db.json')
        try:
            os.makedirs(os.path.dirname(self.path))
            userdb = {
                "_default": {
                    "1": {
                        "name": "Test User",
                        "email": "test@example.com",
                        "userid": "https://example.com/test"
                    },
                    "2": {
                        "name": "Dummy User",
                        "email": "dummy@example.com",
                        "userid": "https://example.com/dummy"
                    },
                }
            }
            with open(self.path, 'w') as f:
                json.dump(userdb, f, ensure_ascii=False, indent=1)
        except Exception as e:
            print("Could not create test user database.")
            print(e)
            sys.exit(1)

    def main(self, *args):
        sys.argv = ["userctl/__main__.py", *args]
        rdamsc_userctl.main()

    def get_last_commit(self):
        try:
            repo = Repo(os.path.dirname(self.path))
        except NotGitRepository:
            repo = Repo.init(os.path.dirname(self.path))
        head = repo.head()
        head_commit = repo.get_object(head)
        return head_commit

    def users(self) -> dict:
        with open(self.path, 'r') as f:
            userdb = json.load(f)
        return userdb.get("_default")

    def apiusers(self) -> dict:
        with open(self.path, 'r') as f:
            userdb = json.load(f)
        return userdb.get("api_users")


@pytest.fixture
def app():
    with tempfile.TemporaryDirectory() as inst_path:
        yield App(inst_path)
