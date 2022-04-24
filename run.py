import asyncio
import inspect
import os
import logging
import platform
import sqlite3
import subprocess
import sys
from threading import Thread

from pyrogram import Client, errors, idle
from pyrogram.errors import RPCError
from pyrogram.handlers import ErrorHandler
from pyrogram.types import Message

from helper.cmd import get_module_name, exception_str
from helper.module import load_modules

logging.basicConfig(level=logging.INFO)


async def error_handler(_, error: Exception, message: Message):
    trace = inspect.trace()
    try:
        name = get_module_name(inspect.getmodule(trace[-1][0]))
        args = (
            error,
            name,
            trace[-1][2],
            " ".join(message.command),
        )
    except AttributeError:
        args = (
            error,
            "Unknown",
            trace[-1][2],
            " ".join(message.command),
        )
    except TypeError:
        args = (
            error,
            get_module_name(inspect.getmodule(trace[-1][0])),
            trace[-1][2],
            "",
        )
    except Exception:
        args = (error, "Unknown", 0, "Unknown")
    txt = exception_str(*args)
    try:
        return await message.edit(txt)
    except RPCError as ex:
        name = ex.ID or ex.NAME
        if name in ["MSG_ID_INVALID", "MESSAGE_ID_INVALID"]:
            try:
                return await message.reply(text=txt)
            except RPCError:
                return


if __name__ == "__main__":
    basepath = os.path.dirname(os.path.realpath(__file__))
    if basepath != os.getcwd():
        os.chdir(basepath)

    import config
    from helper.misc import __version__, modules_dict, build_version

    app = Client(
        "lordnet",
        api_id=config.api_id,
        api_hash=config.api_hash,
        hide_password=True,
        workdir=basepath,
        app_version=__version__,
        device_model=f"lordnet-userbot @ {build_version}",
        system_version=platform.version() + " " + platform.machine(),
        sleep_threshold=30,
        parse_mode="HTML",
    )

    try:
        app.start()
        modules_dict.client = app

        app.add_handler(ErrorHandler(error_handler))
    except sqlite3.OperationalError as e:
        if str(e) == "database is locked":
            if os.name == "posix":
                logging.warning("Session файл заблокирован. Пробую разблокировать...")
                output = subprocess.run(
                    ["fuser", "lordnet.session"], capture_output=True
                ).stdout.decode()
                pid = output.split()[0]
                subprocess.run(["kill", pid])
                os.execvp("python3", ["python3", "run.py"])
            else:
                logging.warning(
                    "Session файл заблокирован. Закройте его вручную (python.*)"
                )
                sys.exit(-1)
        raise e from None
    except (errors.NotAcceptable, errors.Unauthorized) as e:
        logging.error(
            f"{e.__class__.__name__}: {e}\n"
            f"Переношу файл сессии lordnet.session-old..."
        )
        os.rename("./lordnet.session", "./lordnet.session-old")
        os.execvp("python3", ["python3", "run.py"])

    Thread(target=load_modules, args=(asyncio.get_event_loop(),)).start()

    if len(sys.argv) == 4:
        restart_type = sys.argv[3]
        if restart_type == "1":
            text = "<b>💚 lordnet обновлён успешно!</b>"
        else:
            text = "<b>😋 Перезагрузка прошла успешно!</b>"
        try:
            app.send_message(
                chat_id=sys.argv[1], text=text, reply_to_message_id=int(sys.argv[2])
            )
        except errors.RPCError:
            app.send_message(chat_id=sys.argv[1], text=text)

    logging.info("lordnet-userbot запущен!")

    idle()
