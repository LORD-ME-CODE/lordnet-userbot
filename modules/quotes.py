import base64
import logging
import os
from io import BytesIO
from pyrogram import Client, errors, types

from helper import module, session, exception_str, import_library

Image = import_library("PIL.Image", "pillow")
cv2 = import_library("cv2", "opencv-python")


@module(cmds=["q", "quote"], args=["reply"], desc="Создать цитату из сообщения")
async def quote_cmd(client: Client, message: types.Message):
    if len(message.command) > 1 and message.command[1].isdigit():
        count = int(message.command[1])
        if count < 1:
            count = 1
        elif count > 15:
            count = 15
    else:
        count = 1

    is_png = "!png" in message.command or "!file" in message.command
    send_for_me = "!me" in message.command or "!ls" in message.command
    no_reply = "!noreply" in message.command or "!nr" in message.command

    messages = []

    msgs = [
        msg
        async for msg in client.get_chat_history(
            message.chat.id,
            offset_id=-message.reply_to_message_id
            if count == 1 else message.reply_to_message_id,
            limit=count + 1,
        )
    ]
    if count == 1:
        msgs = msgs[::-1]
    print(len(msgs))
    for msg in msgs:
        if msg.empty:
            continue
        if msg.id >= message.id:
            break
        if no_reply:
            msg.reply_to_message = None

        messages.append(msg)

        if len(messages) >= count:
            break

    if send_for_me:
        await message.delete()
        message = await client.send_message("me", "<b>🖼️ Создаю квотес...</b>")
    else:
        await message.edit("<b>🖼️ Создаю квотес...</b>")

    url = "https://quotes.fl1yd.su/generate"
    params = {
        "messages": [
            await render_message(client, msg) for msg in messages if not msg.empty
        ],
        "quote_color": "#162330",
        "text_color": "#fff",
    }

    async with session.post(url, json=params) as response:
        if not response.ok:
            return await message.edit(
                f"<b>Quotes API ошибка!</b>\n" f"<code>{response.text}</code>"
            )
        data = BytesIO(await response.read())
        data.name = "quote.png" if is_png else "quote.webp"
        data.seek(0)

    await message.edit("<b>📸 Отправляю...</b>")

    try:
        func = client.send_document if is_png else client.send_sticker
        chat_id = "me" if send_for_me else message.chat.id
        await func(chat_id, data)
    except errors.RPCError as e:
        await message.edit(exception_str(e))
    else:
        await message.delete()


@module(
    cmds=["fq", "fakequote"],
    args=["args"],
    desc="Создать FAKE цитату из сообщения\n\n(Доступные аргументы: !png = Отправка файлом, !me = Отправка в лс, "
    "!nr = Не отвечать)",
)
async def fake_quote_cmd(client: Client, message: types.Message):
    is_png = "!png" in message.command or "!file" in message.command
    send_for_me = "!me" in message.command or "!ls" in message.command
    no_reply = "!noreply" in message.command or "!nr" in message.command

    fake_quote_text = " ".join(
        [
            arg
            for arg in message.command[1:]
            if arg not in ["!png", "!file", "!me", "!ls", "!noreply", "!nr"]
        ]
    )

    if not fake_quote_text:
        return await message.edit("<b>🌝 Фейк сообщение не указано!</b>")

    q_message = await client.get_messages(message.chat.id, message.reply_to_message.id)
    q_message.text = fake_quote_text
    q_message.entities = None
    if no_reply:
        q_message.reply_to_message = None

    if send_for_me:
        await message.delete()
        message = await client.send_message("me", "<b>🖼️ Создаю квотес...</b>")
    else:
        await message.edit("<b>🖼️ Создаю квотес...</b>")

    url = "https://quotes.fl1yd.su/generate"
    params = {
        "messages": [await render_message(client, q_message)],
        "quote_color": "#162330",
        "text_color": "#fff",
    }

    async with session.post(url, json=params) as response:
        if not response.ok:
            return await message.edit(
                f"<b>Quotes API ошибка!</b>\n" f"<code>{response.text}</code>"
            )
        data = BytesIO(await response.read())
        data.name = "quote.png" if is_png else "quote.webp"
        data.seek(0)

    await message.edit("<b>📸 Отправляю...</b>")

    try:
        func = client.send_document if is_png else client.send_sticker
        chat_id = "me" if send_for_me else message.chat.id
        await func(chat_id, data)
    except errors.RPCError as e:  # no rights to send stickers, etc
        await message.edit(exception_str(e))
    else:
        await message.delete()


# noinspection PyTypeChecker
not_allowed = (
    "audio, document, voice,"
    " contact, location, venue, poll, dice, game".split(", ") + [None]
)


root = os.environ.get("SUDO_UID") and os.geteuid() != 0


async def render_message(app: Client, message: types.Message) -> dict:
    async def get_file(msg) -> str:
        file_name = await app.download_media(
            message=msg,
        )
        if file_name.endswith(".tgs"):
            return ""
        elif file_name.endswith((".webm", ".gif", ".mp4")):
            try:
                vidcap = cv2.VideoCapture(file_name)
                _, image = vidcap.read()
                content = cv2.imencode(".jpg", image)[1].tobytes()
                vidcap.release()
            except Exception as ex:
                logging.warning(ex)
                return ""
        else:
            with open(file_name, "rb") as f:
                content = f.read()
        os.remove(file_name)
        data = base64.b64encode(content).decode()
        return data

    if message.caption:
        text = message.caption
    elif message.poll:
        text = get_poll_text(message.poll)
    elif message.text:
        text = message.text
    elif message.media not in not_allowed:
        text = ""
    else:
        text = get_reply_text(message)

    if message.media not in not_allowed:
        media = await get_file(message)
        if not media:
            text = get_reply_text(message)
    else:
        text = get_reply_text(message)
        media = ""

    entities = []
    if message.entities:
        for entity in message.entities:
            entities.append(
                {
                    "offset": entity.offset,
                    "length": entity.length,
                    "type": str(entity.type),
                }
            )

    def move_forwards(msg: types.Message):
        if msg.forward_from:
            msg.from_user = msg.forward_from
        if msg.forward_sender_name:
            msg.from_user.id = 0
            msg.from_user.first_name = msg.forward_sender_name
            msg.from_user.last_name = ""
        if msg.forward_from_chat:
            msg.sender_chat = msg.forward_from_chat
            msg.from_user.id = 0
        if msg.forward_signature:
            msg.author_signature = msg.forward_signature

    move_forwards(message)

    author = {}
    if message.from_user and message.from_user.id != 0:
        from_user = message.from_user

        author["id"] = from_user.id
        author["name"] = get_full_name(from_user)
        if message.author_signature:
            author["rank"] = message.author_signature
        elif message.chat.type != "supergroup" or message.forward_date:
            author["rank"] = ""
        else:
            try:
                member = await message.chat.get_member(from_user.id)
            except errors.UserNotParticipant:
                author["rank"] = ""
            else:
                author["rank"] = getattr(member, "title", "") or (
                    "owner"
                    if member.status == "creator"
                    else "admin"
                    if member.status == "administrator"
                    else ""
                )

        if from_user.photo:
            author["avatar"] = await get_file(from_user.photo.big_file_id)
        elif not from_user.photo and from_user.username:
            async with session.get(f"https://t.me/{from_user.username}") as res:
                t_me_page = await res.text()
            sub = '<meta property="og:image" content='
            index = t_me_page.find(sub)
            if index != -1:
                link = t_me_page[index + 35 :].split('"')
                if (
                    len(link) > 0
                    and link[0]
                    and link[0] != "https://telegram.org/img/t_logo.png"
                ):
                    async with session.get(link[0]) as res:
                        avatar = res.content
                    author["avatar"] = base64.b64encode(avatar).decode()
                else:
                    author["avatar"] = ""
            else:
                author["avatar"] = ""
        else:
            author["avatar"] = ""
    elif message.from_user and message.from_user.id == 0:
        author["id"] = 0
        author["name"] = message.from_user.first_name
        author["rank"] = ""
    else:
        author["id"] = message.sender_chat.id
        author["name"] = message.sender_chat.title
        author["rank"] = "channel" if message.sender_chat.type == "channel" else ""

        if message.sender_chat.photo:
            author["avatar"] = await get_file(message.sender_chat.photo.big_file_id)
        else:
            author["avatar"] = ""
    author["via_bot"] = message.via_bot.username if message.via_bot else ""

    reply = {}
    reply_msg = message.reply_to_message
    if reply_msg and not reply_msg.empty:
        move_forwards(reply_msg)

        if reply_msg.from_user:
            reply["id"] = reply_msg.from_user.id
            reply["name"] = get_full_name(reply_msg.from_user)
        else:
            reply["id"] = reply_msg.sender_chat.id
            reply["name"] = reply_msg.sender_chat.title

        reply["text"] = get_reply_text(reply_msg)

    return {
        "text": text,
        "media": media,
        "entities": entities,
        "author": author,
        "reply": reply,
    }


def get_audio_text(audio: types.Audio) -> str:
    if audio.title and audio.performer:
        return f" ({audio.title} — {audio.performer})"
    elif audio.title:
        return f" ({audio.title})"
    elif audio.performer:
        return f" ({audio.performer})"
    else:
        return ""


def get_reply_text(reply: types.Message) -> str:
    return (
        "📷 Photo" + ("\n" + reply.caption if reply.caption else "")
        if reply.photo
        else get_reply_poll_text(reply.poll)
        if reply.poll
        else "📍 Геолокация"
        if reply.location or reply.venue
        else "👤 Контакт"
        if reply.contact
        else "🖼 GIF"
        if reply.animation
        else "🎧 Аудио" + get_audio_text(reply.audio)
        if reply.audio
        else "📹 Видео"
        if reply.video
        else "📹 Видеосообщение"
        if reply.video_note
        else "🎵 Голосовое сообщение"
        if reply.voice
        else (reply.sticker.emoji + " " if reply.sticker.emoji else "") + "Стикер"
        if reply.sticker
        else "💾 Файл " + reply.document.file_name
        if reply.document
        else "🎮 Игра"
        if reply.game
        else "🎮 установил новый рекорд"
        if reply.game_high_score
        else f"{reply.dice.emoji} - {reply.dice.value}"
        if reply.dice
        else (
            "👤 присоединился к чату"
            if reply.new_chat_members[0].id == reply.from_user.id
            else "👤 приглашён в чат пользователем %s"
            % (get_full_name(reply.new_chat_members[0]))
        )
        if reply.new_chat_members
        else (
            "👤 вышел из чата"
            if reply.left_chat_member.id == reply.from_user.id
            else "👤 удалён админом %s" % (get_full_name(reply.left_chat_member))
        )
        if reply.left_chat_member
        else f"✏ изменил название чата на {reply.new_chat_title}"
        if reply.new_chat_title
        else "🖼 изменил фото чата"
        if reply.new_chat_photo
        else "🖼 удалил фото чата"
        if reply.delete_chat_photo
        else "📍 закрепил сообщение"
        if reply.pinned_message
        else "🎤 начал новый видеочат"
        if reply.video_chat_started
        else "🎤 завершил видеочат"
        if reply.video_chat_ended
        else "🎤 добавил новых участников видеочата"
        if reply.video_chat_members_invited
        else "👥 создал чат"
        if reply.group_chat_created or reply.supergroup_chat_created
        else "👥 создал канал"
        if reply.channel_chat_created
        else reply.text or "Не поддерживаемое сообщение"
    )


def get_poll_text(poll: types.Poll) -> str:
    text = get_reply_poll_text(poll) + "\n"

    text += poll.question + "\n"
    for option in poll.options:
        text += f"- {option.text}"
        if option.voter_count > 0:
            text += f" ({option.voter_count} voted)"
        text += "\n"

    text += f"Total: {poll.total_voter_count} voted"

    return text


def get_reply_poll_text(poll: types.Poll) -> str:
    if poll.is_anonymous:
        text = (
            "📊 Анонимное голосование"
            if poll.type == "regular"
            else "📊 Анонимная викторина"
        )
    else:
        text = "📊 Голосование" if poll.type == "regular" else "📊 Викторина"
    if poll.is_closed:
        text += " (завершено)"

    return text


def get_full_name(user: types.User) -> str:
    name = user.first_name
    if user.last_name:
        name += " " + user.last_name
    return name
