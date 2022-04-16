from pyrogram.types import Message
from pyrogram import Client

from helper.misc import modules_dict, prefix
from helper.module import module


@module(command="help", description="Help command", args=["module"])
async def help_cmd(_: Client, message: Message):
    if len(message.command) == 1:
        text = (
            "<b>★ List of all available commands (lordnet-userbot)\n"
            f"Help on a specific module: <code>{prefix()}help <b>[module]</b></code></b>\n\n"
        )
        for module_name, module_obj in modules_dict.items():
            commands = module_obj["commands"]
            text += f"<b>☭ {module_name.split('.')[-1].capitalize()}:  </b>"
            if len(commands) > 0:
                text += (
                    " ".join(
                        f'{" ".join(f"<code>{prefix()}" + c + "</code>" for c in cmd["name"])}'
                        for cmd in commands
                    )
                    + "\n"
                )
            else:
                text += "<i>No commands</i>\n"
        text += f"\n<b>⋰ <i>The number of modules in the userbot:</i> {len(modules_dict)}</b>"
        if len(text) >= 2048:
            await message.edit(text[:2048], disable_web_page_preview=True)
            text = text[2048:]
        while len(text) >= 2048:
            await message.reply(text[:2048], disable_web_page_preview=True)
            text = text[2048:]

    else:
        value = modules_dict.get("modules." + message.command[1].lower())
        if value is None:
            text = f"<code>Module <b>{message.command[1]}</b> not found</code>"
        else:
            text = f"Help for <b>{message.command[1]}</b> module:\n\n"
            commands = value["commands"]
            if len(commands) > 0:
                text += (
                    "\n".join(
                        f'<b>{" ".join(f"<code>{prefix()}"+c+"</code>" for c in cmd["name"])}'
                        f' {" ".join("["+c+"]" for c in cmd["args"])}</b>'
                        f'</code> - <i>{cmd["desc"]}</i>'
                        for cmd in commands
                    )
                    + "\n"
                )
            else:
                text += "<i>No commands</i>"
    await message.edit(text)
