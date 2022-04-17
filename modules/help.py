from pyrogram.types import Message
from pyrogram import Client

from helper.misc import modules_dict, prefix
from helper.module import module

from bs4 import BeautifulSoup


@module(command=["help", "h"], description="Помощь по модулям", args=["модуль"])
async def help_cmd(_: Client, message: Message):
    if len(message.command) == 1:
        text = (
            "<b>★ Список всех модулей (<a href='https://t.me/lordnet_userbot'>lordnet-userbot</a>)\n"
            f"Помощь к определённому модулю: <code>{prefix()}help <b>[модуль]</b></code>\n\n"
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
                text += "<i>Нет команд</i>\n"
        text += f"\n<b>⋰ <i>Кол-во модулей в юзерботе:</i> {len(modules_dict)}</b>"
        if len(text) >= 2048:
            text = BeautifulSoup(text, "html.parser").prettify()
            await message.edit(text[:2048], disable_web_page_preview=True)
            text = text[2048:]
        while len(text) >= 2048:
            text = BeautifulSoup(text, "html.parser").prettify()
            await message.reply(text[:2048], disable_web_page_preview=True)
            text = text[2048:]

    else:
        value = modules_dict.get("modules." + message.command[1].lower())
        if value is None:
            value = modules_dict.get("custom." + message.command[1].lower())
        if value is None:
            text = f"<code>Модуль <b>{message.command[1]}</b> не найден</code>"
        else:
            text = f"Помощь для <b>{message.command[1]}</b> модуля:\n\n"
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
                text += "<i>Нет команд</i>"
    await message.edit(text, disable_web_page_preview=True)
