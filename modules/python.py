from io import StringIO
from contextlib import redirect_stdout

from pyrogram import Client
from pyrogram.types import Message

from helper.module import module
from helper.cmd import exception_str, aimport_library


@module(commands=["ex", "exec", "py", "exnoedit"], desc="Execute Python code")
def exec_cmd(client: Client, message: Message):
    if len(message.command) == 1:
        message.edit("<b>✐ Please enter the code you want to run</b>")
        return

    reply = message.reply_to_message

    code = message.text.split(maxsplit=1)[1]
    stdout = StringIO()

    message.edit("<b>✈ Executing code...</b>")

    try:
        with redirect_stdout(stdout):
            exec(code)
        text = (
            "<b>✎ Code:</b>\n"
            f"<code>{code}</code>\n\n"
            "<b>☛ Result</b>:\n"
            f"<code>{stdout.getvalue()}</code>"
        )
        if message.command[0] == "exnoedit":
            message.reply(text)
        else:
            message.edit(text)
    except Exception as e:
        message.edit(exception_str(e))


@module(commands=["ev", "eval"], desc="Eval Python code")
def eval_cmd(client: Client, message: Message):
    if len(message.command) == 1:
        message.edit("<b>✐ Please enter an expression</b>")
        return

    reply = message.reply_to_message

    code = message.text.split(maxsplit=1)[1]

    try:
        result = eval(code)
        message.edit(
            "<b>✎ Expression:</b>\n"
            f"<code>{code}</code>\n\n"
            "<b>☛ Result</b>:\n"
            f"<code>{result}</code>"
        )
    except Exception as e:
        message.edit(exception_str(e))


async def aexec(codea, client, message):
    codea = "async def __todo(message, client, reply): " + "".join(
        f"\n {_l}" for _l in codea.split("\n")
    )
    if "print(" not in codea.replace(" ", ""):
        exec(codea)
        return await locals()["__todo"](message, client, message.reply_to_message)
    else:
        f = StringIO()
        exec(codea)
        with redirect_stdout(f):
            await locals()["__todo"](message, client, message.reply_to_message)
        jj = f.getvalue()
        return jj


# noinspection PyPep8
@module(commands=["aex", "aexec", "aexnoedit"], desc="Async execute python code")
async def aexec_handler(client: Client, message: Message):
    try:
        code = message.text.split(maxsplit=1)[1]
    except:
        code = ""
    if not code:
        return await message.edit("<b>✐ Please enter the code you want to run</b>")
    try:
        await message.edit("<b>✈ Executing code...</b>")
        s = await aexec(code, client, message)
        s = (
            str(s).replace("<", "").replace(">", "")
            if type(s) == str or "<" in str(s) or ">" in str(s)
            else s
        )
        text = (
            f"<b>✎ Code:</b>\n<code>"
            f'{code.replace("<", "").replace(">", "")}'
            "</code>\n\n<b>☛ Result"
            f":</b>\n<code>{s}</code>"
        )
        if message.command[0] == "aexnoedit":
            await message.reply(text)
        else:
            await message.edit(text)
    except Exception as ex:
        return await message.edit(exception_str(ex))


# noinspection PyPep8
@module(commands=["aev", "aeval"], desc="Async evaluate python code")
async def aeval_handler(client: Client, message: Message):
    try:
        code = message.text.split(maxsplit=1)[1]
    except:
        code = ""
    if not code:
        return await message.edit(
            "<b>✐ Please enter the expression you want to run</b>"
        )
    try:
        async_eval = await aimport_library("async_eval")
        aeval = async_eval.eval
        await message.edit("<b>✈ Executing code...</b>")
        s = aeval(
            code,
            {"message": message, "client": client, "reply": message.reply_to_message},
        )
        s = (
            str(s).replace("<", "").replace(">", "")
            if type(s) == str or "<" in str(s) or ">" in str(s)
            else s
        )
        return await message.edit(
            f"<b>✎ Expression:</b>\n<code>"
            f'{code.replace("<", "").replace(">", "")}</code>'
            "\n\n<b>☛ Result"
            f":</b>\n<code>{s}</code>"
        )
    except Exception as ex:
        return await message.edit(exception_str(ex))
