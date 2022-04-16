import os
import sys

from pyrogram.types import Message

from helper.module import module


def restart(message: Message, restart_type):
    text = "1" if restart_type == "update" else "2"
    os.execvp(
        sys.executable,
        [
            sys.executable,
            "run.py",
            f"{message.chat.id}",
            f" {message.message_id}",
            f"{text}",
        ],
    )


@module(commands=["restart", "reload"], desc="Restart the lordnet-userbot")
async def restart_cmd(_, message: Message):
    await message.edit("<b>✇ Restarting...</b>")
    restart(message, "restart")
