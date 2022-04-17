import importlib
import os
import asyncio
import subprocess
import sys
import traceback
from types import ModuleType
from pyrogram import errors


def restart():
    os.execvp(sys.executable, [sys.executable, "run.py"])


def get_module_name(insp: ModuleType):
    return insp.__name__


default_text = "<b>Error! (Report this to @lordnetchat)</b>"


def exception_str(e: Exception):
    traceback.print_exc()
    if isinstance(e, errors.RPCError):
        return (
            f"{default_text}\n"
            f"<code>[{e.CODE} {e.ID or e.NAME}] - {e.MESSAGE}</code>"
        )
    else:
        return f"{default_text}\n" f"<code>{e.__class__.__name__}: {e}</code>"


def import_library(library_name: str, package_name: str = None):
    """
    :param library_name: library name (import example...)
    :param package_name: package name in PyPi (pip install example)
    :return: module
    """

    if package_name is None:
        package_name = library_name

    try:
        _temp = modules_.get(library_name)
        if not _temp:
            _temp = importlib.import_module(library_name)
        return _temp
    except ImportError:
        completed = subprocess.run(
            [sys.executable, "-m", "pip", "install", package_name]
        )
        assert completed.returncode == 0, "library install failed"
        modules_[library_name] = importlib.import_module(library_name)
        return modules_[library_name]


modules_ = {}


async def aimport_library(library_name: str, package_name: str = None):
    """
    :param library_name: library name (import example...)
    :param package_name: package name in PyPi (pip install example)
    :return: module
    """

    if package_name is None:
        package_name = library_name

    try:
        _temp = modules_.get(library_name)
        if not _temp:
            _temp = importlib.import_module(library_name)
        return _temp
    except ImportError:
        completed = await asyncio.create_subprocess_exec(
            sys.executable,
            "-m",
            "pip",
            "install",
            package_name,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        assert completed.returncode == 0, "library install failed"
        modules_[library_name] = importlib.import_module(library_name)
        return modules_[library_name]
