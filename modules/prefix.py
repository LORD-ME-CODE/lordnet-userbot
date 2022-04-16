from pyrogram.types import Message

from helper.misc import set_prefix
from helper.module import module, load_modules


@module(commands=["setprefix", "setprefix_lordnet"], description="Set prefix for lordnet-userbot")
async def setprefix(_, message: Message):
    if len(message.command) > 1:
        pref = message.command[1]
        set_prefix(pref)
        await message.edit(f"<b>Prefix [ <code>{pref}</code> ] is set!</b>")
        load_modules()
    else:
        await message.edit("<b>The prefix must not be empty!</b>")