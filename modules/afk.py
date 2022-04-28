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

import datetime
from time import time

from pyrogram import filters
from pyrogram.types import Message

from helper.module import module
from helper.db import db


_afk = db.get("afk", {"status": False, "reason": "Сплю...", "start": 0})


is_afk = filters.create(lambda _, __, ___: _afk["status"])


users = {}


@module(
    is_afk
    & (filters.private | filters.mentioned)
    & ~filters.channel
    & ~filters.me
    & ~filters.bot
)
async def afk(_, message: Message):
    now = users.get(message.from_user.id, 0)
    if time() - now > 39:
        users[message.from_user.id] = time()

        start = datetime.datetime.fromtimestamp(_afk["start"])
        end = datetime.datetime.now().replace(microsecond=0)
        afk_time = end - start
        text = (
            "<b>😴 Я AFK сейчас.\n" "⏳ Уже прошло: <code>{}</code>\n" "Причина: {}</b>"
        ).format(afk_time, _afk["reason"])
        return await message.reply(text)


@module(commands=["afk", "unafk"], desc="Включить AFK", args=["причина"])
async def afk_cmd(_, message: Message):
    now = not _afk["status"]
    _afk["status"] = now
    if len(message.command) > 1:
        _afk["reason"] = message.text.split(maxsplit=1)[1]
    if now:
        _afk["start"] = int(datetime.datetime.now().timestamp())
        text = "<b>AFK</b> режим включён\n" "Причина: <b>{}</b>".format(_afk["reason"])
    else:
        start = datetime.datetime.fromtimestamp(_afk["start"])
        end = datetime.datetime.now().replace(microsecond=0)
        afk_time = end - start
        text = "<b>🙂 Вы больше не AFK.\n" "Прошло: <code>{}</code></b>".format(afk_time)
    db.set("afk", _afk)

    await message.edit(text)
