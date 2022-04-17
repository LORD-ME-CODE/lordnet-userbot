from helper import module, Message, Client


@module(cmds=["uinfo", "userinfo", "user", "u"], desc="Get user information")
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
                f"<b>User <copy>{message.command[1]}</copy> not found</b>"
            )
    else:
        user = message.from_user

    text = (
        "<b><u>👤 User INFO</u>:\n"
        "<b>└ Permlink:</b> {}\n"
        "<b>└ 🆔:</b> <code>{}</code>\n"
        "<b>└ First N:</b> <code>{}</code>\n"
        "<b>└ Last N:</b> <code>{}</code>\n"
        "<b>└ Username:</b> <code>{}</code>\n"
        "<b>└ Language:</b> <code>{}</code>\n"
        "<b>└ 📞 Number:</b> {}\n"
        "<b>└ 📍 Status:</b> <u>{}</u>\n"
        "<b>└ 📅 Online:</b> <code>{}</code>\n"
        "<b>└ 🤖 Bot:</b> <code>{}</code>\n"
        "<b>└ 🔨 Restricted:</b> <code>{}</code>\n"
        "<b>└ ✅ Verified:</b> <code>{}</code>\n"
        "<b>└ 🧑‍💻 Support:</b> <code>{}</code>\n"
        "<b>└ 🙈 Fake:</b> <code>{}</code>\n"
        "<b>└ ⛔ Scam:</b> <code>{}</code>"
    ).format(
        user.mention,
        user.id,
        user.first_name.replace("<", "&lt;").replace(">", "&gt;"),
        user.last_name.replace("<", "&lt;").replace(">", "&gt;"),
        user.username,
        user.language_code,
        "<code>" + str(user.phone_number) + "</code>"
        if not user.is_self
        else "<spoiler>LMAO</spoiler>",
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


@module(cmds=["cuser", "cu", "copyuser"], desc="Copy user avatar and info")
async def copyuser(client: Client, message: Message):
    """
    Copy user avatar and info
    """
    if message.reply_to_message:
        user = message.reply_to_message.from_user
    elif len(message.command) > 1:
        user = await client.get_users(message.command[1])
        if not user:
            return await message.edit(
                f"<b>User <copy>{message.command[1]}</copy> not found</b>"
            )
    else:
        return await message.edit("<b>🙈 Reply to a user or mention them</b>")

    await client.update_profile(first_name=user.first_name, last_name=user.last_name)
    await client.download_media(user.photo.big_file_id, "downloads/copyuser.jpg")
    await client.set_profile_photo(photo="downloads/copyuser.jpg")

    await client.send_message(
        "me",
        "<b>📸 Copied user avatar and info</b>",
    )
