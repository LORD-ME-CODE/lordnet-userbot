import datetime
from time import time

from pyrogram import filters
from pyrogram.types import Message

from helper.module import module
from helper.db import db


_afk = db.get("afk", {"status": False, "reason": "Sleeping...", "start": 0})


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
        text = "<b>😴 I'm AFK now.\n" "I'm were in AFK: <code>{}</code></b>".format(
            afk_time
        )
        return await message.reply(text)


@module(commands=["afk", "unafk"], desc="Set yourself as AFK", args=["reason"])
async def afk_cmd(_, message: Message):
    now = not _afk["status"]
    _afk["status"] = now
    if len(message.command) > 1:
        _afk["reason"] = message.text.split(maxsplit=1)[1]
    if now:
        _afk["start"] = int(datetime.datetime.now().timestamp())
        text = "<b>AFK</b> mode is now enabled\n" "Reason: <b>{}</b>".format(
            _afk["reason"]
        )
    else:
        start = datetime.datetime.fromtimestamp(_afk["start"])
        end = datetime.datetime.now().replace(microsecond=0)
        afk_time = end - start
        text = (
            "<b>🙂 You are no longer AFK.\n"
            "You were in AFK: <code>{}</code></b>".format(afk_time)
        )
    db.set("afk", _afk)

    await message.edit(text)
