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

from helper import module, Message, prefix
from asyncio import sleep


@module(commands="say", args=["задержка", "текст"], desc="Сказать с анимацией")
async def say(_, message: Message):
    if len(message.command) < 2:
        return await message.edit(
            f"<b>🎙️ Пожалуйста используйте: <code>{prefix()}say [задержка]* [текст]*</code></b>"
        )
    try:
        delay = float(message.command[1])
        split = 2
    except ValueError:
        delay = 0.1
        split = 1
    text = message.text.split(maxsplit=split)[split]
    try:
        chunks = [
            text[i : i + len(text) // 5] for i in range(0, len(text), len(text) // 5)
        ]
    except ValueError:
        chunks = text
    text = ""

    async def edit(chunx):
        nonlocal text
        text += chunx
        try:
            await message.edit(text)
        except:
            pass

    for chunk in chunks:
        await edit(chunk)
        await sleep(delay)
