from git import Repo
from .db import db


class ModulesDict(dict):
    def __init__(self, **items):
        super().__init__(items)
        self.__dict = None

    def __setitem__(self, module: str, value: dict):
        if module in self.__dict:
            raise KeyError(f"Module {module} already exists")
        self.__dict[module] = value

    def __getitem__(self, module: str):
        if module not in self.__dict:
            raise KeyError(f"Module {module} does not exist")
        return self.__dict[module]


modules_dict = ModulesDict()


git = Repo(".")
commits_from_repo = list(git.iter_commits())
result = len(commits_from_repo)
top = int(result // 1000)
ver = int((result % 1000) // 100)
bottom = int((result % 1000) % 100)
__version__ = f"{top}.{ver}.{bottom}"

prefix = db.get("prefix", ".")
