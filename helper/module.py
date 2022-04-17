import inspect
import logging
import os
from importlib import import_module
from pathlib import Path

import pyrogram

from helper.cmd import get_module_name
from helper.misc import modules_dict, prefix
from helper.misc import session, lordnet_url


def get_commands(x: tuple):
    return x[0] if len(x) > 0 and isinstance(x[0], list) else None


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
        if filters:
            dec = modules_dict.client.on_message(*filters)
        else:
            dec = modules_dict.client.on_message(
                pyrogram.filters.command(commands, prefix()) & pyrogram.filters.me
            )
    else:
        dec = modules_dict.client.on_message(*filters)

    def sub_decorator(func):
        if inspect.iscoroutinefunction(func):

            @dec
            async def wrapper(*args, **kwargs):
                return await func(*args, **kwargs)

        else:

            @dec
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

        return wrapper

    return sub_decorator


def load_modules():
    modules_dict.clear()

    imported = 0
    exceptions = 0

    for path in sorted(sorted((Path("modules")).rglob("*.py")), key=os.path.getmtime):
        module_path = ".".join(path.parent.parts + (path.stem,))
        try:
            import_module(module_path)
            imported += 1
        except Exception as e:
            exceptions += 1
            logging.warning(
                f"Не удалось импортировать {module_path}: {e.__class__.__name__}: {e}"
            )

    for path in sorted(sorted((Path("custom")).rglob("*.py")), key=os.path.getmtime):
        module_path = ".".join(path.parent.parts + (path.stem,))
        try:
            import_module(module_path)
            imported += 1
        except Exception as e:
            exceptions += 1
            logging.warning(
                f"Не удалось импортировать {module_path}: {e.__class__.__name__}: {e}"
            )

    logging.info(f"Загружено {imported} модулей")
    if exceptions:
        logging.warning(f"{exceptions} модулей не удалось загрузить")


async def module_exists(module_name: str):
    try:
        avaiable_modules = await session.get(lordnet_url + "all")
        return module_name in await avaiable_modules.text()
    except:
        return False


async def load_module(module_name: str):
    import_module("custom." + module_name)
