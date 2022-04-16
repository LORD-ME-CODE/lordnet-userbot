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
@module(commands=["sysinfo", "sys", "sinfo"])
async def sysinfo_cmd(_, message: Message):
    await message.edit("<b>😇 Getting system info...</b>")

    text = (
        "<b>⚙️ Usage:\n"
        "    <u>• CPU</u>: {} Cores ({}%)\n"
        "    <u>• RAM:</u> {}/{} ({}%)\n\n"
        "💻 System INFO:\n"
        "    <u>• OS:</u> {}\n"
        "    <u>• Kernel:</u> {}\n"
        "    <u>• Arch:</u> {}\n"
        "    <u>• Version:</u> {}\n\n"
        "📦 Python:\n"
        "    <u>• Version:</u> {}\n"
        "    <u>• lordnet:</u> {}\n"
        "    <u>• GitPython:</u> {}\n"
        "    <u>• Pip:</u> {}</b>"
    )

    info = [
        psutil.cpu_count(logical=True),
        round(psutil.cpu_percent(interval=None)),
        round(
            (psutil.virtual_memory().total - psutil.virtual_memory().available)
            / 1024
            / 1024,
        ),
        round(psutil.virtual_memory().total / 1024 / 1024),
        round(psutil.virtual_memory().percent),
    ]
    try:
        if os.name == "posix":
            system = os.popen("cat /etc/*release").read()
            b = system.find('DISTRIB_DESCRIPTION="') + 21
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
