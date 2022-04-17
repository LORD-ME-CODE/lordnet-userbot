from pyrogram.types import Message

from helper.misc import set_prefix
from helper.module import module
from helper.cmd import restart


@module(
    commands=["setprefix", "setprefix_lordnet"],
    args=["символ"],
    description="Установить префикс для lordnet-userbot",
)
def prefix_cmd(_, message: Message):
    if len(message.command) > 1:
        pref = message.command[1]
        set_prefix(pref)
        message.edit(f"<b>Префикс 『 <code>{pref}</code> 』 установлен!</b>")
        restart()
    else:
        message.edit("<b>Префикс не может быть пустым!</b>")
