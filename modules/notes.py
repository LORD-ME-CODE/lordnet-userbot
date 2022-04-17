from pyrogram import filters, errors, Client
from pyrogram.types import (
    InputMediaPhoto,
    InputMediaVideo,
    InputMediaAudio,
    InputMediaDocument,
)

from helper import module, Message, db, prefix
from modules.python import aexec_handler


@module(commands="save", args=["название", "reply/text"], desc="Создать заметку")
async def save_note(client: Client, message: Message):
    await message.edit("<b>🔃 Загрузка...</b>")

    try:
        chat = await client.get_chat(db.get("chat_id", 0))
    except (errors.RPCError, ValueError, KeyError):
        chat = await client.create_supergroup(
            "🧛‍♂️ lordnet-userbot заметки",
            "Не трогайте этот чат пожалуйста и не удаляйте его!",
        )
        db.set("chat_id", chat.id)

    chat_id = chat.id

    if message.reply_to_message and len(message.text.split()) >= 2:
        note_name = message.text.split(maxsplit=1)[1]
        if message.reply_to_message.media_group_id:
            checking_note = db.get(f"note{note_name}", False)
            if not checking_note:
                get_media_group = [
                    _.message_id
                    for _ in await client.get_media_group(
                        message.chat.id, message.reply_to_message.message_id
                    )
                ]
                try:
                    message_id = await client.forward_messages(
                        chat_id, message.chat.id, get_media_group
                    )
                except errors.ChatForwardsRestricted:
                    await message.edit(
                        "<b>⛔ Пересылка сообщений запрещена админами чата</b>"
                    )
                    return
                note = {
                    "MESSAGE_ID": str(message_id[1].message_id),
                    "MEDIA_GROUP": True,
                    "CHAT_ID": str(chat_id),
                }
                db.set(f"note{note_name}", note)
                await message.edit(f"<b>📝 Заметка {note_name} сохранена</b>")
            else:
                await message.edit("<b>😋 Такая заметка уже существует</b>")
        else:
            checking_note = db.get(f"note{note_name}", False)
            if not checking_note:
                try:
                    message_id = await message.reply_to_message.forward(chat_id)
                except errors.ChatForwardsRestricted:
                    if message.reply_to_message.text:
                        message_id = await client.send_message(
                            chat_id, message.reply_to_message.text
                        )
                    else:
                        await message.edit(
                            "<b>⛔ Пересылка сообщений запрещена админами чата</b>"
                        )
                        return
                note = {
                    "MEDIA_GROUP": False,
                    "MESSAGE_ID": str(message_id.message_id),
                    "CHAT_ID": str(chat_id),
                }
                db.set(f"note{note_name}", note)
                await message.edit(f"<b>📝 Заметка {note_name} сохранена</b>")
            else:
                await message.edit("<b>😋 This note already exists</b>")
    elif len(message.text.split()) >= 3:
        note_name = message.text.split(maxsplit=1)[1].split()[0]
        checking_note = db.get(f"note{note_name}", False)
        if not checking_note:
            message_id = await client.send_message(
                chat_id, message.text.split(note_name)[1].strip()
            )
            note = {
                "MEDIA_GROUP": False,
                "MESSAGE_ID": str(message_id.message_id),
                "CHAT_ID": str(chat_id),
            }
            db.set(f"note{note_name}", note)
            await message.edit(f"<b>📝 Заметка {note_name} сохранена</b>")
        else:
            await message.edit("<b>😋 Такая заметка уже существует</b>")
    else:
        await message.edit(
            f"<b>Пример: <code>{prefix()}save название_заметки</code></b>"
        )


@module(cmds="note", args=["name"], desc="Получить заметку")
async def note_send(client: Client, message: Message):
    if len(message.text.split()) >= 2:
        await message.edit("<b>🔃 Загрузка...</b>")

        note_name = f"{message.text.split(maxsplit=1)[1]}"
        find_note = db.get(f"note{note_name}", False)
        if find_note:
            try:
                await client.get_messages(
                    int(find_note["CHAT_ID"]), int(find_note["MESSAGE_ID"])
                )
            except errors.RPCError:
                await message.edit(
                    "<b>Извините, но эта заметка недоступна.\n\n"
                    f"Вы можете удалить эту заметку с помощью "
                    f"<code>{prefix}clear {note_name}</code></b>"
                )
                return

            if find_note.get("MEDIA_GROUP"):
                messages_grouped = await client.get_media_group(
                    int(find_note["CHAT_ID"]), int(find_note["MESSAGE_ID"])
                )
                media_grouped_list = []
                for _ in messages_grouped:
                    if _.photo:
                        if _.caption:
                            media_grouped_list.append(
                                InputMediaPhoto(_.photo.file_id, _.caption.markdown)
                            )
                        else:
                            media_grouped_list.append(InputMediaPhoto(_.photo.file_id))
                    elif _.video:
                        if _.caption:
                            if _.video.thumbs:
                                media_grouped_list.append(
                                    InputMediaVideo(
                                        _.video.file_id,
                                        _.video.thumbs[0].file_id,
                                        _.caption.markdown,
                                    )
                                )
                            else:
                                media_grouped_list.append(
                                    InputMediaVideo(_.video.file_id, _.caption.markdown)
                                )
                        elif _.video.thumbs:
                            media_grouped_list.append(
                                InputMediaVideo(
                                    _.video.file_id, _.video.thumbs[0].file_id
                                )
                            )
                        else:
                            media_grouped_list.append(InputMediaVideo(_.video.file_id))
                    elif _.audio:
                        if _.caption:
                            media_grouped_list.append(
                                InputMediaAudio(_.audio.file_id, _.caption.markdown)
                            )
                        else:
                            media_grouped_list.append(InputMediaAudio(_.audio.file_id))
                    elif _.document:
                        if _.caption:
                            if _.document.thumbs:
                                media_grouped_list.append(
                                    InputMediaDocument(
                                        _.document.file_id,
                                        _.document.thumbs[0].file_id,
                                        _.caption.markdown,
                                    )
                                )
                            else:
                                media_grouped_list.append(
                                    InputMediaDocument(
                                        _.document.file_id, _.caption.markdown
                                    )
                                )
                        elif _.document.thumbs:
                            media_grouped_list.append(
                                InputMediaDocument(
                                    _.document.file_id, _.document.thumbs[0].file_id
                                )
                            )
                        else:
                            media_grouped_list.append(
                                InputMediaDocument(_.document.file_id)
                            )
                if message.reply_to_message:
                    await client.send_media_group(
                        message.chat.id,
                        media_grouped_list,
                        reply_to_message_id=message.reply_to_message.message_id,
                    )
                else:
                    await client.send_media_group(message.chat.id, media_grouped_list)
            elif message.reply_to_message:
                await client.copy_message(
                    message.chat.id,
                    int(find_note["CHAT_ID"]),
                    int(find_note["MESSAGE_ID"]),
                    reply_to_message_id=message.reply_to_message.message_id,
                )
            else:
                await client.copy_message(
                    message.chat.id,
                    int(find_note["CHAT_ID"]),
                    int(find_note["MESSAGE_ID"]),
                )
            await message.delete()
        else:
            await message.edit("<b>⛔ Нет такой заметки</b>")
    else:
        await message.edit(f"<b>Пример: <code>{prefix}note название_заметки</code></b>")


@module(
    cmds=["exnote", "notexec"],
    args=["name"],
    desc="Выполнить код из заметки с помощью Python",
)
async def exnote_send(client: Client, message: Message):
    if len(message.text.split()) >= 2:
        await message.edit("<b>🔃 Загрузка...</b>")

        note_name = f"{message.text.split(maxsplit=1)[1]}"
        find_note = db.get(f"note{note_name}", False)
        if find_note:
            try:
                nmessage = await client.get_messages(
                    int(find_note["CHAT_ID"]), int(find_note["MESSAGE_ID"])
                )
            except errors.RPCError:
                await message.edit(
                    "<b>Извините, но эта заметка недоступна.\n\n"
                    f"Вы можете удалить эту заметку с помощью "
                    f"<code>{prefix}clear {note_name}</code></b>"
                )
                return
            if nmessage.text:
                text = "exec " + nmessage.text
            elif nmessage.caption:
                text = "exec " + nmessage.caption
            else:
                return await message.edit(
                    "<b>🐍 Эта заметка не содержит кода Python.</b>"
                )
            message.text = text
            return await aexec_handler(client, message)
        else:
            await message.edit("<b>⛔ Нет такой заметки</b>")
    else:
        await message.edit(
            f"<b>Пример: <code>{prefix}exnote название_заметки</code></b>"
        )


@module(cmds="notes", desc="Показать все заметки")
async def notes(_, message: Message):
    await message.edit("<b>Loading...</b>")
    text = "<b>📃 Доступные заметки:</b>\n\n"
    collection = db.get_collection()
    for note in collection.keys():
        if note[:4] == "note":
            text += f"<code>{note[4:]}</code>\n"
    await message.edit(text)


@module(cmds="clear", args=["name"], desc="Удалить заметку")
async def clear_note(_, message: Message):
    if len(message.text.split()) >= 2:
        note_name = message.text.split(maxsplit=1)[1]
        find_note = db.get(f"note{note_name}", False)
        if find_note:
            db.remove(f"note{note_name}")
            await message.edit(f"<b>🗑️ Заметка {note_name} удалена</b>")
        else:
            await message.edit("<b>⛔ Нет такой заметки</b>")
    else:
        await message.edit(
            f"<b>Пример: <code>{prefix}clear название_заметки</code></b>"
        )
