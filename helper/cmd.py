import importlib
import os
import asyncio
import subprocess
import sys
import inspect
import traceback
from types import ModuleType
from pyrogram import errors


def restart():
    os.execvp(sys.executable, [sys.executable, "run.py"])


def get_module_name(insp: ModuleType):
    return insp.__name__


default_text = "<b>Ошибка в модуле <u>{}</u>! (Репортните в @lordnetchat)</b>\n\n"


def exception_str(e: Exception):
    line = str(traceback.extract_stack()[-1][1])
    traceback.print_exc()

    module_name = get_module_name(inspect.getmodule(inspect.stack()[1][0]))
    if isinstance(e, errors.RPCError):
        return (
            f"{default_text.format(module_name)}\n"
            f"<code>[{e.CODE} {e.ID or e.NAME}] - {e.MESSAGE}</code>  <b>(Строка {line})</b>"
        )
    else:
        return (
            f"{default_text.format(module_name)}\n"
            f"<code>{e.__class__.__name__}: {e}</code>  <b>(Строка {line})</b>"
        )


def import_library(library_name: str, package_name: str = None):
    """
    :param library_name: название модуля (import pyrogram...)
    :param package_name: название либы в PyPi (pip install pyrogram)
    :return: module
    """

    if package_name is None:
        package_name = library_name.replace("_", "-")

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
    :param library_name: название модуля (import pyrogram...)
    :param package_name: название либы в PyPi (pip install pyrogram)
    :return: module
    """

    if package_name is None:
        package_name = library_name.replace("_", "-")

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
