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

from helper.misc import python_version, __version__, modules_dict
from helper.misc import build_version, build_link, c_date
from helper.module import module


@module(commands=["info", "ver", "v", "version"], desc="Информация о юзерботе")
async def info(_, message: Message):
    """
    Info command
    """

    text = (
        '<b><a href="https://t.me/lordnet_userbot">✉ lordnet-userbot</a> ИНФО:\n\n'
        f"☛ lordnet версия: <code>{__version__}</code>\n"
        f"🧱 Билд: <a href='{build_link}'>{build_version}</a> ({c_date})\n"
        f"🐍 Python версия: <code>{python_version}</code>\n\n"
        f"🎲 Модули: @lordnet_modules\n"
        f"☛ Кол-во модулей: <code>{len(modules_dict)}</code>\n\n"
        f"📃 Лицензия: <a href='https://github.com/LORD-ME-CODE/lordnet-userbot/blob/main/LICENSE'>GNU v3.0</a>\n"
        f"☛ Репо: <a href='https://github.com/LORD-ME-CODE/lordnet-userbot'>lordnet-userbot</a>\n\n"
        f"☛ Канал: @lordnet_userbot\n"
        f"☛ Чат: @lordnetchat\n"
        f"☛ Кодер: @lord_code</b>"
    )

    return await message.edit(text, disable_web_page_preview=True)
