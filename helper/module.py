import inspect

import pyrogram

from helper.cmd import get_module_name
from helper.misc import modules_dict, prefix


def module(*filters, **params):
    if not params and not filters:
        raise IndexError("None of the arguments are specified")

    commands = params.get("command") or params.get("commands")
    if isinstance(commands, str):
        commands = [commands]
    elif isinstance(commands, list):
        commands = commands
    elif (
        not isinstance(commands, list) and not isinstance(commands, str) and not filters
    ):
        raise TypeError("commands must be a list or a string")

    module_value = get_module_name(inspect.getmodule(inspect.stack()[1][0]))

    if module_value not in modules_dict:
        modules_dict[module_value] = {
            "commands": [],
        }

    if commands:
        modules_dict[module_value]["commands"].append(
            {
                "name": commands,
                "desc": params.get("desc")
                or params.get("description")
                or "Module without description",
                "args": params.get("args") or params.get("arguments") or [],
            }
        )
        dec = modules_dict.client.on_message(
            pyrogram.filters.command(commands, prefix) & pyrogram.filters.me
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
