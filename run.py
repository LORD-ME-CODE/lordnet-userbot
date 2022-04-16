import os
import logging
import platform
import sqlite3
import subprocess
import sys
from importlib import import_module
from pathlib import Path

from pyrogram import Client, errors, idle

logging.basicConfig(level=logging.INFO)


if __name__ == "__main__":
    basepath = os.path.dirname(os.path.realpath(__file__))
    if basepath != os.getcwd():
        os.chdir(basepath)

    import config
    from helper.misc import __version__, git, modules_dict

    app = Client(
        "lordnet",
        api_id=config.api_id,
        api_hash=config.api_hash,
        hide_password=True,
        workdir=basepath,
        app_version=__version__,
        device_model=f"lordnet-userbot @ {git.head.commit.hexsha[:7]}",
        system_version=platform.version() + " " + platform.machine(),
        sleep_threshold=30,
        parse_mode="HTML",
    )

    try:
        app.start()
        modules_dict.client = app
    except sqlite3.OperationalError as e:
        if str(e) == "database is locked" and os.name == "posix":
            logging.warning(
                "Session file is locked. Trying to kill blocking process..."
            )
            output = subprocess.run(
                ["fuser", "lordnet.session"], capture_output=True
            ).stdout.decode()
            pid = output.split()[0]
            subprocess.run(["kill", pid])
            os.execvp("python3", ["python3", "run.py"])
        raise e from None
    except (errors.NotAcceptable, errors.Unauthorized) as e:
        logging.error(
            f"{e.__class__.__name__}: {e}\n"
            f"Moving session file to lordnet.session-old..."
        )
        os.rename("./lordnet.session", "./lordnet.session-old")
        os.execvp("python3", ["python3", "run.py"])

    for path in sorted((Path("modules")).rglob("*.py")):
        module_path = ".".join(path.parent.parts + (path.stem,))
        try:
            module = import_module(module_path)
        except Exception as e:
            logging.warning(
                f"Can't import module {module_path}: {e.__class__.__name__}: {e}"
            )

    if len(sys.argv) == 4:
        restart_type = sys.argv[3]
        if restart_type == "1":
            text = "<b>Userbot updated successfully!</b>"
        else:
            text = "<b>Restart completed successfully!</b>"
        try:
            app.send_message(
                chat_id=sys.argv[1], text=text, reply_to_message_id=int(sys.argv[2])
            )
        except errors.RPCError:
            app.send_message(chat_id=sys.argv[1], text=text)

    logging.info("lordnet-userbot started!")

    idle()
