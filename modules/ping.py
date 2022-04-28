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

from time import perf_counter_ns
from pyrogram.types import Message
from helper.module import module


@module(commands=["ping", "p"], description="Проверить пинг")
async def ping_cmd(_, message: Message):
    start = perf_counter_ns()
    await message.edit("<b>☘️ Понг!</b>")
    end = perf_counter_ns()
    res = round((end - start) * 0.000001, 3)
    await message.edit(f"<b>🍀 Ваш пинг: {res}мс</b>")
