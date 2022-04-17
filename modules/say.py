from helper import module, Message, prefix
from asyncio import sleep


@module(commands="say", args=["delay", "text"], desc="Say with animated text")
async def say(_, message: Message):
    if len(message.command) < 3:
        return await message.edit(
            f"<b>🎙️ Please use: <code>{prefix()}say [delay]* [text]*</code></b>"
        )
    try:
        delay = float(message.command[1])
    except ValueError:
        delay = 0.1
    text = message.text.split(maxsplit=2)[2]
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
        await message.edit(text)

    for chunk in chunks:
        await edit(chunk)
        await sleep(delay)
