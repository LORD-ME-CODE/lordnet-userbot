import asyncio
from time import perf_counter

from pyrogram import Client
from pyrogram.types import Message

from helper.module import module

PIPE = asyncio.subprocess.PIPE


@module(cmds=["shell", "sh"], args=["команда"], desc="Выполнить консольную команду")
async def shell_cmd(_: Client, message: Message):
    if len(message.command) < 2:
        return await message.edit("<b>✖ Вы не указали команду.</b>")
    cmd_text = message.text.split(maxsplit=1)[1]
    cmd_obj = await asyncio.create_subprocess_shell(
        cmd_text,
        stdout=PIPE,
        stderr=PIPE,
        
    )
    text = f"<b>≻</b> <code>{cmd_text}</code>\n\n"

    await message.edit(text + "<b>Выполняю...</b>")
    try:
        start_time = perf_counter()
        stdout, stderr = await cmd_obj.communicate()
    except Exception as ex:
        text += "<b>✖ Error:\n<code>{ex}</code></b>"
    else:
        stop_time = perf_counter()
        if stdout:
            text += "<b>⌬ Вывод:</b>\n" f"<code>{stdout}</code>\n\n"
        if stderr:
            text += "<b>✖ Ошибка:</b>\n" f"<code>{stderr}</code>\n\n"
        text += f"<b>Выполнено за {round(stop_time - start_time, 5)} сек. | Код ({cmd_obj.returncode})</b>"
    await message.edit(text)
    cmd_obj.kill()


@module(
    cmds=["shinput", "shin"],
    args=["команда", "input={текст}"],
    desc="Выполнить консольную команду с вводом",
)
async def shell_input_cmd(_: Client, message: Message):
    if len(message.command) < 2:
        return await message.edit("<b>✖ Вы не указали команду.</b>")
    cmd_text = message.text.split(maxsplit=1)[1]
    try:
        inp = cmd_text.split("input=", maxsplit=1)[1]
        cmd_text = cmd_text.split("input=" + inp, maxsplit=1)[0]
    except IndexError:
        return await message.edit("<b>✖ Вы не указали входной текст.</b>")
    cmd_obj = await asyncio.create_subprocess_shell(
        cmd_text,
        stdout=PIPE,
        stderr=PIPE,
        stdin=PIPE,
        
    )
    text = f"<b>≻</b> <code>{cmd_text}</code>\n\n"

    await message.edit(text + "<b>Выполняю...</b>")
    try:
        start_time = perf_counter()
        stdout, stderr = await cmd_obj.communicate(input=inp)
    except Exception as ex:
        text += "<b>✖ Error:\n<code>{ex}</code></b>"
    else:
        stop_time = perf_counter()
        if stdout:
            text += "<b>⌬ Вывод:</b>\n" f"<code>{stdout}</code>\n\n"
        if stderr:
            text += "<b>✖ Ошибка:</b>\n" f"<code>{stderr}</code>\n\n"
        text += f"<b>Выполнено за {round(stop_time - start_time, 5)} сек. | Код ({cmd_obj.returncode})</b>"
    await message.edit(text)
    cmd_obj.kill()
