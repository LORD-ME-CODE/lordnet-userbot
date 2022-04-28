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

from pyrogram.types import Message

from helper.misc import set_prefix
from helper.module import module
from helper.cmd import restart


@module(
    commands=["setprefix", "setprefix_lordnet"],
    args=["символ"],
    description="Установить префикс для lordnet-userbot",
)
def prefix_cmd(_, message: Message):
    if len(message.command) > 1:
        pref = message.command[1]
        set_prefix(pref)
        message.edit(f"<b>Префикс 『 <code>{pref}</code> 』 установлен!</b>")
        restart()
    else:
        message.edit("<b>Префикс не может быть пустым!</b>")
