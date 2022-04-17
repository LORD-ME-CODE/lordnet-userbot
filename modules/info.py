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
        f"☛ Билд: <a href="{build_link}">{build_version}</a> ({c_date})\n\n"
        f"☛ Python версия: <code>{python_version}</code>\n"
        f"☛ Кол-во модулей: <code>{len(modules_dict)}</code>\n"
        f"☛ Лицензия: <a href='https://github.com/LORD-ME-CODE/lordnet-userbot/blob/main/LICENSE'>GNU v3.0</a>\n"
        f"☛ Канал: @lordnet_userbot\n"
        f"☛ Чат: @lordnetchat\n"
        f"☛ Репо: <a href='https://github.com/LORD-ME-CODE/lordnet-userbot'>lordnet-userbot</a>\n"
        f"☛ Кодер: @lord_code</b>"
    )

    return await message.edit(text, disable_web_page_preview=True)
