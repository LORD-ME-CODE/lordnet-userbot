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

from helper import module, Message, Client, escape_html


@module(
    cmds=["uinfo", "userinfo", "user", "u"], args=["name/id/reply"], desc="Инфа о юзере"
)
async def userinfo(client: Client, message: Message):
    """
    Get user information
    """
    if message.reply_to_message:
        user = message.reply_to_message.from_user
    elif len(message.command) > 1:
        user = await client.get_users(message.command[1])
        if not user:
            return await message.edit(
                f"<b>Юзер <copy>{message.command[1]}</copy> не найден</b>"
            )
    else:
        user = message.from_user

    text = (
        "<b><u>👤 Юзер ИНФО</u>:\n"
        "<b>└ Пермалинк:</b> {}\n"
        "<b>└ 🆔:</b> <code>{}</code>\n"
        "<b>└ Имя:</b> <code>{}</code>\n"
        "<b>└ Фамилия:</b> <code>{}</code>\n"
        "<b>└ Ник:</b> <code>{}</code>\n"
        "<b>└ Язык:</b> <code>{}</code>\n"
        "<b>└ 📞 Номер:</b> {}\n"
        "<b>└ 📍 Статус:</b> <u>{}</u>\n"
        "<b>└ 📅 Онлайн:</b> <code>{}</code>\n"
        "<b>└ 🤖 Бот:</b> <code>{}</code>\n"
        "<b>└ 🔨 Ограниченный:</b> <code>{}</code>\n"
        "<b>└ ✅ Верифнутый:</b> <code>{}</code>\n"
        "<b>└ 🧑‍💻 Сапорт:</b> <code>{}</code>\n"
        "<b>└ 🙈 Фейк:</b> <code>{}</code>\n"
        "<b>└ ⛔ Скам:</b> <code>{}</code>"
    ).format(
        user.mention,
        user.id,
        escape_html(user.first_name),
        escape_html(user.last_name),
        user.username,
        user.language_code,
        "<code>" + str(user.phone_number) + "</code>"
        if not user.is_self
        else "<spoiler>ЛОХ</spoiler>",
        user.status,
        user.last_online_date,
        user.is_bot,
        user.is_restricted,
        user.is_verified,
        user.is_support,
        user.is_fake,
        user.is_scam,
    )

    return await message.edit(text)


first_name, last_name = None, None


@module(cmds=["cuser", "cu", "copyuser"], desc="Скопировать аватарку и инфу о юзере")
async def copyuser(client: Client, message: Message):
    global first_name, last_name
    if message.reply_to_message:
        user = message.reply_to_message.from_user
    elif len(message.command) > 1:
        user = await client.get_users(message.command[1])
        if not user:
            return await message.edit(
                f"<b>Юзер <copy>{message.command[1]}</copy> не найден</b>"
            )
    else:
        return await message.edit(
            "<b>🙈 Ответьте на сообщение юзера или тэгните его</b>"
        )

    await message.delete()

    if not first_name:
        me = await client.get_me()
        first_name = me.first_name
        last_name = me.last_name
        photo_id = me.photo.big_file_id
        await client.download_media(photo_id, "downloads/copyuser_me.jpg")

    await client.update_profile(first_name=user.first_name, last_name=user.last_name)
    await client.download_media(user.photo.big_file_id, "downloads/copyuser.jpg")
    await client.set_profile_photo(photo="downloads/copyuser.jpg")

    await client.send_message(
        "me",
        f"<b>📸 Успешно скопирован юзер {user.mention} аватарка и информация</b>",
    )


@module(cmds=["undo"], desc="Вернуть свою инфу и аватарку в профиль")
async def undo(client: Client, message: Message):
    if first_name:
        await client.update_profile(first_name=first_name, last_name=last_name)
        try:
            await client.set_profile_photo(photo="downloads/copyuser_me.jpg")
        except:
            pass

    await message.edit(
        f"<b>📸 Инфа и аватарка успешно восстановлена.</b>",
    )
