from pyrogram.types import Message

from helper.misc import python_version, __version__, modules_dict
from helper.module import module


@module(commands=["info", "ver", "v", "version"], desc="Userbot info")
async def info(_, message: Message):
    """
    Info command
    """

    text = (
        '<b><a href="https://t.me/lordnet_userbot">✉ lordnet-userbot</a> INFO:\n\n'
        f"☛ Python version: <code>{python_version}</code>\n"
        f"☛ lordnet version: <code>{__version__}</code>\n"
        f"☛ Modules count: <code>{len(modules_dict)}</code>\n"
        f"☛ License: <a href='https://github.com/LORD-ME-CODE/lordnet-userbot/blob/main/LICENSE'>GNU v3.0</a>"
        f"</b>"
    )

    return await message.edit(text)
