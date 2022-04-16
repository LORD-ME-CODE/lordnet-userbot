import os
import subprocess
import sys

from pyrogram.types import Message

from helper.cmd import exception_str
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


@module(commands=["update"], desc="Update the lordnet-userbot")
async def update_cmd(_, message: Message):
    try:
        await message.edit("<b>✇ Updating pip...</b> (<code>25%</code>)")
        subprocess.run([sys.executable, "-m", "pip", "install", "-U", "pip"])
        await message.edit(
            "<b>✇ Updating setuptools and wheel...</b>"
            " (<code>50%</code>)"
        )
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-U", "setuptools", "wheel"]
        )
        await message.edit(
            "<b>✇ Updating userbot from git...</b>"
            " (<code>75%</code>)"
        )
        subprocess.run(["git", "pull"])
        await message.edit(
            "<b>✇ Updating from requirements.txt<code>...</code>"
            "(<code>95%</code>)</b>"
        )
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-U", "-r", "requirements.txt"]
        )
        await message.edit(
            "<b>✔ Update completed successfully, restarting userbot...</b>"
        )
    except Exception as e:
        await message.edit(exception_str(e))
    else:
        restart(message, "update")
