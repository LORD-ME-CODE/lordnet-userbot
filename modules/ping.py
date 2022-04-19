from time import perf_counter_ns
from pyrogram.types import Message
from helper.module import module


@module(commands=["ping", "p"], description="Проверить пинг")
async def ping_cmd(_, message: Message):
    start = perf_counter_ns()
    await message.edit("<b>☘️ Понг!</b>")
    end = perf_counter_ns()
    res = round((end - start) * 0.000001, 3)
    await message.edit(f"<b>🍀 Ваш пинг: {res}мс</b>")
