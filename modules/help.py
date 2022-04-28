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

from pyrogram.types import Message
from pyrogram import Client

from helper.misc import modules_dict, prefix
from helper.module import module


@module(command=["help", "h"], description="Помощь по модулям", args=["модуль/команда"])
async def help_cmd(_: Client, message: Message):
    if len(message.command) == 1:
        text = (
            "<b>★ Список всех модулей (<a href='https://t.me/lordnet_userbot'>lordnet-userbot</a>)\n"
            f"Помощь к определённому модулю: <code>{prefix()}help <b>[модуль]</b></code>\n\n"
        )
        msg_edited = False
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
            if len(text) >= 2048:
                if msg_edited:
                    await message.reply(text=text, disable_web_page_preview=True)
                else:
                    await message.edit(text, disable_web_page_preview=True)
                    msg_edited = True
                text = ""

        text += f"\n<b>⋰ <i>Кол-во модулей в юзерботе:</i> {len(modules_dict)}</b>"
        if msg_edited:
            await message.reply(text, disable_web_page_preview=True)
        else:
            await message.edit(text, disable_web_page_preview=True)
    else:
        value = modules_dict.get("modules." + message.command[1].lower())
        if value is None:
            value = modules_dict.get("custom." + message.command[1].lower())
        if value is None:
            value = modules_dict.commands.get(message.command[1].lower())
            if value is None:
                text = f"<b>🧭 Модуль <code>{message.command[1]}</code> не найден</b>"
            else:
                text = f"🐍 Помощь для <b>{message.command[1]}</b> команды:\n\n"
                text += (
                    f"<b><code>{prefix()}{message.command[1]}"
                    f'</code> {" ".join("[" + c + "]" for c in value["args"])}</b>\n'
                    f'<i>{value["desc"]}</i>\n'
                )
                text += f'\n<b>🍂 Модуль: {value["module"].split(".")[-1]}</b>'
        else:
            text = f"🐍 Помощь для <b>{message.command[1]}</b> модуля:\n\n"
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
                text += "<i>Нет команд</i>\n"
            text += f'\n<b>🍂 Автор:</b> {value["made_by"]}'
        await message.edit(text, disable_web_page_preview=True)
