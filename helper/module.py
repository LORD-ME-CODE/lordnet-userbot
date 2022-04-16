import inspect
import logging
import os
from importlib import import_module
from pathlib import Path

import pyrogram
# noinspection PyUnresolvedReferences
from pyrogram.types import Message  # Shortcut for modules

from helper.cmd import get_module_name
from helper.misc import modules_dict, prefix


def get_commands(x: tuple):
    return x[0] if len(x) > 0 and isinstance(x[0], list) else None


# noinspection PyIncorrectDocstring
def module(*filters, **params):
    """
    Decorator for handling lordnet-userbot

    Parameters:
        filters (``Any``, *optional*):
            Pyrogram filters to be used for the command.
        commands (``list or str``, *required if filters is not used*):
            List of commands to be handled by the module or single command.
        description (``str``, *optional*):
            Description of the module.
        args (``list or str``, *optional*):
            Args to be passed to the module.
    """

    if not params and not filters:
        raise IndexError("None of the arguments are specified")

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
        raise TypeError("commands must be a list or a string")

    module_value = get_module_name(inspect.getmodule(inspect.stack()[1][0]))

    if not modules_dict.module_in(module_value):
        modules_dict[module_value] = {
            "commands": [],
        }

    if commands:
        modules_dict.add_command(
            module_value,
            {
                "name": commands,
                "desc": params.get("desc")
                or params.get("description")
                or "Module without description",
                "args": params.get("args") or params.get("arguments") or [],
            },
        )
        if filters:
            dec = modules_dict.client.on_message(
                pyrogram.filters.command(commands, prefix()) & filters
            )
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

    for path in sorted(sorted((Path("modules")).rglob("*.py")), key=os.path.getmtime):
        module_path = ".".join(path.parent.parts + (path.stem,))
        try:
            import_module(module_path)
        except Exception as e:
            logging.warning(
                f"Can't import module {module_path}: {e.__class__.__name__}: {e}"
            )
