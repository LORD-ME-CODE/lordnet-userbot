import os
import subprocess
import sys

from pyrogram.types import Message

from helper.misc import Git, build_version, __version__, prefix
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


@module(commands=["restart", "reload"], desc="Перезагрузить lordnet-userbot")
async def restart_cmd(_, message: Message):
    await message.edit("<b>✇ Перезагружаю...</b>")
    restart(message, "restart")


@module(commands=["update"], desc="Обновить lordnet-userbot")
async def update_cmd(_, message: Message):
    await message.edit("<b>👩‍🚀 Обновляю pip...</b> (<code>25%</code>)")
    subprocess.run([sys.executable, "-m", "pip", "install", "-U", "pip"])
    await message.edit(
        "<b>👩‍🚀 Обновляю setuptools и wheel...</b>" " (<code>50%</code>)"
    )
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-U", "setuptools", "wheel"]
    )
    await message.edit("<b>👩‍🚀 Обновляю юзербот с гитхаба...</b>" " (<code>75%</code>)")
    subprocess.run(["git", "pull"])
    await message.edit(
        "<b>👩‍🚀 Обновляю либы с requirements.txt<code>...</code>"
        "(<code>95%</code>)</b>"
    )
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-U", "-r", "requirements.txt"]
    )
    await message.edit("<b>👩‍🚀 Обновление завершено, перезагружаю юзербот...</b>")
    restart(message, "update")


@module(commands=["check"], desc="Проверить наличие обновления 👩‍🚀")
async def check_cmd(_, message: Message):
    await message.edit("<b>🧭 Проверяю наличие обновления...</b>")
    head: str = Git().ls_remote(
        "https://github.com/LORD-ME-CODE/lordnet-userbot.git", heads=True
    )
    if not head.startswith(build_version):
        text = (
            f"<b>🟠 Доступно обновление [~{__version__[:-1] + str(int(__version__[-1]) + 1)}]!\n\n"
            f"🔃 Для обновы, введите: <code>{prefix()}update</code></b>"
        )
    else:
        text = "<b>🟢 У вас самая актуальная версия!</b>"
    await message.edit(text)
