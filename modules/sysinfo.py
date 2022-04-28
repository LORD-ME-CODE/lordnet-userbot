#
#  _    ___  ___ ___  _  _ ___ _____    _   _ ___ ___ ___ ___  ___ _____
# | |  / _ \| _ \   \| \| | __|_   _|__| | | / __| __| _ \ _ )/ _ \_   _|
# | |_| (_) |   / |) | .` | _|  | ||___| |_| \__ \ _||   / _ \ (_) || |
# |____\___/|_|_\___/|_|\_|___| |_|     \___/|___/___|_|_\___/\___/ |_|
#
#                            © Copyright 2022
#
#                       https://t.me/lordnet_userbot
#
# 🔒 Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

import platform

from helper import Message, module, python_version, __version__
import psutil
import os
import subprocess
import sys


def git_python():
    if os.name == "nt":
        value = (
            subprocess.getoutput(f"{sys.executable} -m pip freeze | findstr GitPython")
            .split("==")[1]
            .split("\n")[0]
        )
    else:
        value = (
            subprocess.getoutput(f"{sys.executable} -m pip freeze | grep GitPython")
            .split("==")[1]
            .split("\n")[0]
        )
    return value


# noinspection PyBroadException
@module(commands=["sysinfo", "sys", "sinfo"], desc="Информация о системе")
async def sysinfo_cmd(_, message: Message):
    await message.edit("<b>😇 Получаю системную инфу...</b>")

    text = (
        "<b>⚙️ Использование:\n"
        "    <u>• CPU</u>: {} Ядер ({}%)\n"
        "    <u>• ОЗУ:</u> {}/{} ({}%)\n\n"
        "💻 Система:\n"
        "    <u>• ОС:</u> {}\n"
        "    <u>• Kernel:</u> {}\n"
        "    <u>• Арч:</u> {}\n"
        "    <u>• Версия:</u> {}\n\n"
        "📦 Python:\n"
        "    <u>• Версия:</u> {}\n"
        "    <u>• lordnet:</u> {}\n"
        "    <u>• GitPython:</u> {}\n"
        "    <u>• Pip:</u> {}</b>"
    )

    info = []

    try:
        info.append(psutil.cpu_count(logical=True))
    except:
        info.append("n/a")

    try:
        info.append(round(psutil.cpu_percent(interval=None)))
    except:
        info.append("n/a")

    try:
        info.append(
            round(
                (psutil.virtual_memory().total - psutil.virtual_memory().available)
                / 1024
                / 1024,
            )
        )
    except:
        info.append("n/a")

    try:
        info.append(round(psutil.virtual_memory().total / 1024 / 1024))
    except:
        info.append("n/a")

    try:
        info.append(round(psutil.virtual_memory().percent))
    except:
        info.append("n/a")

    try:
        if os.name == "posix":
            system = os.popen("cat /etc/*release").read()
            b = system.find('DISTRIB_DESCRIPTION="') + 21
            # noinspection PyPep8
            system = system[b : system.find('"', b)]
            system = system.replace("<", "").replace(">", "")
        else:
            system = None
        if not system:
            raise Exception
        info.append(system)
    except Exception:
        try:
            system = platform.system()
            info.append(system)
        except Exception:
            info.append("n/a")
    try:
        info.append(platform.release().replace("<", "").replace(">", ""))
    except Exception:
        info.append("n/a")
    try:
        info.append(platform.architecture()[0].replace("<", "").replace(">", ""))
    except Exception:
        info.append("n/a")

    try:
        info.append(platform.version().replace("<", "").replace(">", ""))
    except Exception:
        info.append("n/a")

    dop_info = [
        python_version,
        __version__,
        git_python(),
        subprocess.getoutput(f"{sys.executable} -m pip --version").split()[1].strip(),
    ]
    info += dop_info

    await message.edit(text.format(*info))
