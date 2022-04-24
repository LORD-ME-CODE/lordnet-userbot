import asyncio
import logging
import os
from importlib import import_module
from pathlib import Path

import pyrogram
from pyrogram.handlers import MessageHandler
from helper.misc import modules_dict, prefix
from helper.misc import session, lordnet_url
from typing import Any
from errors import *


def get_commands(x: tuple):
    return x[0] if len(x) > 0 and isinstance(x[0], (list, tuple)) else None


# noinspection PyIncorrectDocstring
def module(*filters, **params):
    """
    Декоратор для модулей lordnet-userbot

    Parameters:
        filters (``Any``, *optional*):
            Пирограм фильтры для модуля.
        commands (``list or str``, *required if filters is not used*):
            Список команд или одна команда для модуля.
        description (``str``, *optional*):
            Описание команд (показывается в help)
        args (``list or str``, *optional*):
            Аргументы для команды (показывается в help)
    """

    if not params and not filters:
        raise IndexError("Не указаны аргументы для модуля")
    elif filters and isinstance(filters[0], str):
        logging.warning(
            "Вы не указали ничего в @module декораторе, проверьте пожалуйста."
        )

    commands = (
        params.get("commands")
        or params.get("command")
        or params.get("cmds")
        or get_commands(filters)
    )
    if isinstance(commands, str):
        commands = [commands]
    elif isinstance(commands, list):
        commands = commands
    elif (
        not isinstance(commands, list) and not isinstance(commands, str) and not filters
    ):
        raise TypeError("Команды должны быть типа строка или список")

    module_value = get_module_name(inspect.getmodule(inspect.stack()[1][0]))

    if not modules_dict.module_in(module_value):
        modules_dict[module_value] = {
            "commands": [],
        }

    insp = False

    if commands:
        args = params.get("args") or params.get("arguments") or []
        if isinstance(args, str):
            args = [args]
        modules_dict.add_command(
            module_value,
            {
                "name": commands,
                "desc": params.get("desc")
                or params.get("description")
                or "Без описания",
                "args": args,
            },
        )
        if not filters:
            filters = pyrogram.filters.command(commands, prefix()) & pyrogram.filters.me
        else:
            insp = True
    else:
        insp = True

    if isinstance(filters, (list, tuple)) and len(filters) == 1:
        filters = filters[0]

    def sub_decorator(func):
        is_coroutine = inspect.iscoroutinefunction(func)
        if insp:
            if is_coroutine:

                async def wrapper(*xds, **kwargs):
                    try:
                        return await func(*xds, **kwargs)
                    except (pyrogram.ContinuePropagation, pyrogram.StopPropagation):
                        raise pyrogram.ContinuePropagation
                    except Exception as ex:
                        return await error_handler_async(error=ex, *xds, **kwargs)

            else:

                def wrapper(*xds, **kwargs):
                    try:
                        return func(*xds, **kwargs)
                    except (pyrogram.ContinuePropagation, pyrogram.StopPropagation):
                        raise pyrogram.ContinuePropagation
                    except Exception as ex:
                        return error_handler_async(error=ex, *xds, **kwargs)

            return wrapper
        if is_coroutine:

            async def wrapper(*xds, **kwargs):
                try:
                    return await func(*xds, **kwargs)
                except Exception as ex:
                    return await error_handler_async(error=ex, *xds, **kwargs)

        else:

            def wrapper(*xds, **kwargs):
                try:
                    return func(*xds, **kwargs)
                except Exception as ex:
                    return error_handler_async(error=ex, *xds, **kwargs)

        handler = MessageHandler(wrapper, filters)
        if "handlers" not in modules_dict[module_value]:
            modules_dict[module_value]["handlers"] = []
        modules_dict.client.add_handler(handler)
        modules_dict[module_value]["handlers"].append(handler)

    return sub_decorator


def load_modules(loop=None):
    if loop:
        asyncio.set_event_loop(loop)

    imported = 0
    exceptions = 0

    for path in sorted(sorted((Path("modules")).rglob("*.py")), key=os.path.getmtime):
        module_path = ".".join(path.parent.parts + (path.stem,))
        try:
            import_module(module_path)
            modules_dict[module_path]["made_by"] = "@lordnet_userbot"
            imported += 1
        except Exception as e:
            exceptions += 1
            logging.warning(
                f"Не удалось импортировать {module_path}: {e.__class__.__name__}: {e}"
            )

    for path in sorted(sorted((Path("custom")).rglob("*.py")), key=os.path.getmtime):
        module_path = ".".join(path.parent.parts + (path.stem,))
        try:
            load_module(module_path)
            imported += 1
        except Exception as e:
            exceptions += 1
            logging.warning(
                f"Не удалось импортировать {module_path}: {e.__class__.__name__}: {e}"
            )

    logging.info(f"Загружено {imported} модулей")
    if exceptions:
        logging.warning(f"{exceptions} модулей не удалось загрузить")


def load_module(module_name: str):
    mod = import_module(module_name, package="__main__")
    made_by = getattr(mod, "made_by", "@Неизвестный")[:64]
    modules_dict[module_name]["made_by"] = made_by


async def unload_module(module_name: str):
    try:
        handlers = modules_dict[module_name]["handlers"]
        for handler in handlers:
            modules_dict.client.remove_handler(handler)
        modules_dict.remove(module_name)
    except KeyError:
        pass


async def all_off_modules():
    avaiable_modules = await session.get(lordnet_url + "all")
    if not avaiable_modules.ok:
        return []
    text = await avaiable_modules.text()
    return text.strip().split("\n")


async def module_exists(module_name: str):
    return module_name in await all_off_modules()


def escape_html(text: Any) -> str:
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
