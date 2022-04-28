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

from io import BytesIO

from helper import module, session, Message


link = "https://webshot.deam.io/{}{}"


@module(cmds=["webshot", "ws"], args=["url", "size"], desc="Скриншот сайта")
async def webshot_cmd(_, message: Message):
    if len(message.command) == 1:
        return await message.edit(
            "<b>⛔ Вы не указали сайт который нужно скриншотить</b>"
        )
    await message.edit("<b>📸 Создание скриншота...</b>")
    splits = message.text.split(maxsplit=2)[1:]
    url = splits[0]
    try:
        size = (
            ""
            if len(splits) == 1
            else "?width={}&height={}".format(*splits[1].split("x"))
        )
    except:
        size = ""
    async with session.get(link.format(url, size)) as response:
        if response.status != 200:
            return await message.edit(f"<b>⛔ Ошибка API, проверьте свои аргументы.</b>")
        image = BytesIO(await response.read())
        image.name = "screen.jpg"
        image.seek(0)
    await message.reply_document(document=image)
