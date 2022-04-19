from time import perf_counter
from pyrogram.types import Message
from helper.module import module


@module(commands=["ping", "p"], description="Проверить пинг")
async def ping_cmd(_, message: Message):
    start = perf_counter()
    await message.edit("<b>○ Понг!</b>")
    end = perf_counter()
    res = round((end - start) * 0.000001, 3)
    await message.edit(f"<b>● Понг! {res}мс</b>")
