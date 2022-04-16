from time import perf_counter
from pyrogram.types import Message
from helper.module import module


@module(commands=['ping', 'p'])
async def ping_cmd(_, message: Message):
    start = perf_counter()
    await message.edit("<b>☻ Pong!</b>")
    end = round((perf_counter() - start) * 1000)
    await message.edit(f"<b>☺ Pong! {end}ms</b>")
