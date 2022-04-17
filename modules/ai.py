import random

from helper import module, Message
from pyrogram import filters
from pyrogram.filters import create
from pyrogram import ContinuePropagation
from helper import db

answers = db.get("answers", {})
status = db.get("status", {})


async def for_answer_func(_, __, message: Message):
    if not status.get(str(message.chat.id)) or str(message.chat.id) not in answers:
        return False
    text = message.text or message.caption
    answer = 0
    x = text.lower().split()
    for i in x:
        for z in answers[str(message.chat.id)].keys():
            if i in z:
                answer += 1
    if (len(x) / 2 >= 3 and answer >= 3) or (len(x) / 2 < 3 and answer >= 1):
        return True
    return False


for_answer = create(for_answer_func)

status_filter = create(lambda _, __, message: status.get(message.chat.id))


@module((filters.caption | filters.text) & ~filters.me & for_answer)
async def ai_handler(_, message: Message):
    text = message.text or message.caption
    answer = []
    for i in text.lower().split():
        for z, v in answers[str(message.chat.id)].items():
            if i in z:
                answer.append(v)
    if answer:
        await message.reply(random.choice(answer))

    raise ContinuePropagation


@module(status_filter & (filters.caption | filters.text) & filters.reply)
async def ai_handler_status(_, message: Message):
    text = message.reply_to_message.text or message.reply_to_message.caption
    if text:
        reply = message.text or message.caption
        if str(message.chat.id) not in answers:
            answers[str(message.chat.id)] = {}
        answers[str(message.chat.id)][text.lower()] = reply.lower()
        db.set("answers", answers)
    raise ContinuePropagation


@module(commands=["ai"], desc="Enable/Disable ai mode")
async def ai_mode(_, message: Message):
    now = not status.get(str(message.chat.id))
    status[str(message.chat.id)] = now
    db.set("status", status)
    await message.edit(
        f'<code>AI mode for this chat is now</code> <b>{"Enabled ✅" if now else "Disabled ⛔"}</b>'
    )
