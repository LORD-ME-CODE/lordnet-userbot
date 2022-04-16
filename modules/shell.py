from subprocess import Popen, PIPE, TimeoutExpired
from time import perf_counter

from pyrogram import Client
from pyrogram.types import Message

from helper.module import module


@module(cmds=["shell", "sh"], desc="Run shell command")
async def shell_cmd(_: Client, message: Message):
    if len(message.command) < 2:
        return await message.edit("<b>✖ You have not entered a command.</b>")
    cmd_text = message.text.split(maxsplit=1)[1]
    cmd_obj = Popen(
        cmd_text,
        shell=True,
        stdout=PIPE,
        stderr=PIPE,
        text=True,
    )
    text = f"<b>≻</b> <code>{cmd_text}</code>\n\n"

    await message.edit(text + "<b>Doing...</b>")
    try:
        start_time = perf_counter()
        stdout, stderr = cmd_obj.communicate(timeout=60)
    except TimeoutExpired:
        text += "<b>✖ TimeoutExpired (60 seconds)</b>"
    else:
        stop_time = perf_counter()
        if stdout:
            text += "<b>⌬ Output:</b>\n" f"<code>{stdout}</code>\n\n"
        if stderr:
            text += "<b>✖ Error:</b>\n" f"<code>{stderr}</code>\n\n"
        text += f"<b>Done in {round(stop_time - start_time, 5)} second(s) | Code ({cmd_obj.returncode})</b>"
    await message.edit(text)
    cmd_obj.kill()
