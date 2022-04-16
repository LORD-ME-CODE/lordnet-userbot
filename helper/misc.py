from git import Repo
from .db import db


class ModulesDict(dict):
    def __init__(self, **items):
        super().__init__(items)
        self.__dict = {}
        self.client = None

    def items(self):
        return sorted(self.__dict.items(), key=lambda x: x[0].lower())

    def get(self, key):
        return self.__dict.get(key)

    def add_command(self, module: str, command: dict):
        self.__dict[module]["commands"].append(command)

    def module_in(self, module: str) -> bool:
        return module in self.__dict

    def __setitem__(self, module: str, value: dict):
        self.__dict[module] = value

    def __getitem__(self, module: str):
        if module not in self.__dict:
            raise KeyError(f"Module {module} does not exist")
        return self.__dict[module]

    def __str__(self):
        return str(self.__dict)

    def __len__(self):
        return len(self.__dict)


modules_dict = ModulesDict()


git = Repo(".")
commits_from_repo = list(git.iter_commits())
result = len(commits_from_repo)
top = int(result // 1000)
ver = int((result % 1000) // 100)
bottom = int((result % 1000) % 100)
__version__ = f"{top}.{ver}.{bottom}"

prefix = db.get("prefix", ",")
