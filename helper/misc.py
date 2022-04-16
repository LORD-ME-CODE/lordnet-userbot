from __future__ import annotations

import asyncio
from sys import version_info

from git import Repo
from pyrogram import Client

from .db import db

from aiohttp import ClientSession


class ModulesDict(dict):
    def __init__(self, **items):
        super().__init__(items)
        self.__dict = {}
        self.client: Client | None = None

    def items(self):
        return self.__dict.items()

    def get(self, key):
        return self.__dict.get(key)

    def clear(self):
        self.__dict.clear()

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

_prefix_ = db.get("prefix", ",")


def prefix():
    return _prefix_


def set_prefix(new: str):
    db.set("prefix", new)
    global _prefix_
    _prefix_ = prefix


python_version = f"{version_info[0]}.{version_info[1]}.{version_info[2]}"

session = ClientSession()

lordnet_url = (
    asyncio.get_event_loop()
    .run_until_complete(
        session.get(
            "https://github.com/LORD-ME-CODE/lordnet-userbot/blob/main/base_url.txt"
        )
    )
    .text
)
