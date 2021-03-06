#
#  _    ___  ___ ___  _  _ ___ _____    _   _ ___ ___ ___ ___  ___ _____
# | |  / _ \| _ \   \| \| | __|_   _|__| | | / __| __| _ \ _ )/ _ \_   _|
# | |_| (_) |   / |) | .` | _|  | ||___| |_| \__ \ _||   / _ \ (_) || |
# |____\___/|_|_\___/|_|\_|___| |_|     \___/|___/___|_|_\___/\___/ |_|
#
#                            © Copyright 2022
#
#                       https://t.me/lordnet_userbot
#
# 🔒 Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

from __future__ import annotations

from sys import version_info

from git import Repo

# noinspection PyUnresolvedReferences
from git.cmd import Git
from pyrogram import Client

from .db import db

from aiohttp import ClientSession

import os.path


class ModulesDict(dict):
    def __init__(self, **items):
        super().__init__(items)
        self.__dict = {}
        self.client: Client | None = None
        self.commands: dict = {}
        self.deleted: list = []

    def items(self):
        return self.__dict.items()

    def get(self, key):
        return self.__dict.get(key)

    def clear(self):
        self.__dict.clear()

    def remove(self, module: str):
        del self.__dict[module]

    def add_command(self, module: str, command: dict):
        self.__dict[module]["commands"].append(command)
        self.commands.update(
            {
                i: {
                    "args": command["args"],
                    "desc": command["desc"],
                    "module": module,
                }
                for i in command["name"]
            }
        )

    def module_in(self, module: str) -> bool:
        return module in self.__dict

    def __setitem__(self, module: str, value: dict):
        self.__dict[module] = value

    def __getitem__(self, module: str):
        if module not in self.__dict:
            raise KeyError(f"Модуль {module} не найден.")
        return self.__dict[module]

    def __str__(self):
        return str(self.__dict)

    def __len__(self):
        return len(self.__dict)


modules_dict = ModulesDict()


if not os.path.exists("downloads"):
    os.mkdir("downloads")
if not os.path.exists("custom"):
    os.mkdir("custom")


git = Repo(".")
result = int(git.git.rev_list("--count", "HEAD"))
top = int(result // 1000)
ver = int((result % 1000) // 100)
bottom = int((result % 1000) % 100)
__version__ = f"{top}.{ver}.{bottom}"
c_hexed = git.head.object.hexsha

build_version = git.git.rev_parse(c_hexed, short=True)
c_date = git.head.object.committed_datetime
base_link = "https://github.com/LORD-ME-CODE/lordnet-userbot"
build_link = base_link + "/commit/{}".format(c_hexed)

_prefix_ = db.get("prefix", ".")


def prefix():
    return _prefix_


def set_prefix(new: str):
    db.set("prefix", new)
    global _prefix_
    _prefix_ = prefix


python_version = f"{version_info[0]}.{version_info[1]}.{version_info[2]}"

session = ClientSession()

lordnet_url = "https://raw.githubusercontent.com/LORD-ME-CODE/modules/master/lordnet/"
