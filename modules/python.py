from io import StringIO
from contextlib import redirect_stdout

from pyrogram import Client
from pyrogram.types import Message

from helper.module import module, escape_html
from helper.cmd import exception_str, aimport_library


@module(
    commands=["ex", "exec", "py", "exnoedit"], args=["код"], desc="Выполнить Python код"
)
def exec_cmd(client: Client, message: Message):
    if len(message.command) == 1:
        message.edit("<b>✐ Вы не указали код для выполнения</b>")
        return

    reply = message.reply_to_message

    code = message.text.split(maxsplit=1)[1]
    stdout = StringIO()

    message.edit("<b>✈ Выполняю код...</b>")

    try:
        with redirect_stdout(stdout):
            exec(code)
        text = (
            "<b>✎ Код:</b>\n"
            f"<code>{code}</code>\n\n"
            "<b>☛ Результат</b>:\n"
            f"<code>{escape_html(stdout.getvalue())}</code>"
        )
    except Exception as e:
        text = (
            "<b>✎ Код:</b>\n"
            f"<code>{code}</code>\n\n"
            "<b>✘ Ошибка</b>:\n"
            f"<code>{e.__class__}: {escape_html(e)}</code>"
        )
    if message.command[0] == "exnoedit":
        message.reply(text)
    else:
        message.edit(text)


@module(commands=["ev", "eval"], args=["код"], desc="Выполнить Python выражение")
def eval_cmd(client: Client, message: Message):
    if len(message.command) == 1:
        message.edit("<b>✐ Вы не указали выражение для выполнения</b>")
        return

    reply = message.reply_to_message

    code = message.text.split(maxsplit=1)[1]

    try:
        result = eval(code)
        text = (
            "<b>✎ Выражение:</b>\n"
            f"<code>{code}</code>\n\n"
            "<b>☛ Результат</b>:\n"
            f"<code>{escape_html(result)}</code>"
        )
    except Exception as e:
        text = (
            "<b>✎ Выражение:</b>\n"
            f"<code>{code}</code>\n\n"
            "<b>✘ Ошибка</b>:\n"
            f"<code>{e.__class__}: {escape_html(e)}</code>"
        )
    message.edit(text)


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
@module(
    commands=["aex", "aexec", "aexnoedit"],
    args=["код"],
    desc="Асинк выполнение python кода",
)
async def aexec_handler(client: Client, message: Message):
    try:
        code = message.text.split(maxsplit=1)[1]
    except:
        code = ""
    if not code:
        return await message.edit("<b>✐ Вы не указали код для выполнения</b>")
    try:
        await message.edit("<b>✈ Выполняю код...</b>")
        s = await aexec(code, client, message)
        s = escape_html(s)
        text = (
            f"<b>✎ Код:</b>\n<code>"
            f"{escape_html(code)}"
            "</code>\n\n<b>☛ Результат"
            f":</b>\n<code>{s}</code>"
        )
    except Exception as ex:
        text = (
            f"<b>✎ Код:</b>\n<code>"
            f"{escape_html(code)}"
            "</code>\n\n<b>✘ Ошибка"
            f":</b>\n<code>{ex.__class__}: {escape_html(ex)}</code>"
        )
    if message.command[0] == "aexnoedit":
        await message.reply(text)
    else:
        await message.edit(text)


# noinspection PyPep8
@module(
    commands=["aev", "aeval"], args=["код"], desc="Асинк выполнение python выражения"
)
async def aeval_handler(client: Client, message: Message):
    try:
        code = message.text.split(maxsplit=1)[1]
    except:
        code = ""
    if not code:
        return await message.edit("<b>✐ Вы не указали выражение для выполнения</b>")
    try:
        async_eval = await aimport_library("async_eval")
        aeval = async_eval.eval
        await message.edit("<b>✈ Выполняю выражение...</b>")
        s = aeval(
            code,
            {"message": message, "client": client, "reply": message.reply_to_message},
        )
        s = escape_html(s)
        text = (
            f"<b>✎ Выражение:</b>\n<code>"
            f'{code.replace("<", "").replace(">", "")}</code>'
            "\n\n<b>☛ Результат"
            f":</b>\n<code>{s}</code>"
        )
    except Exception as ex:
        text = (
            f"<b>✎ Выражение:</b>\n<code>"
            f'{code.replace("<", "").replace(">", "")}</code>'
            "\n\n<b>✘ Ошибка"
            f":</b>\n<code>{ex.__class__}: {escape_html(ex)}</code>"
        )
    await message.edit(text)
