from pyrogram.types import Message

from helper.misc import set_prefix
from helper.module import module
from helper.cmd import restart


@module(commands=["setprefix", "setprefix_lordnet"], description="Set prefix for lordnet-userbot")
def prefix_cmd(_, message: Message):
    if len(message.command) > 1:
        pref = message.command[1]
        set_prefix(pref)
        message.edit(f"<b>Prefix [ <code>{pref}</code> ] is set!</b>")
        restart()
    else:
        message.edit("<b>The prefix must not be empty!</b>")
