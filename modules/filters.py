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

from pyrogram import Client, filters, ContinuePropagation, errors
from pyrogram.types import (
    Message,
    InputMediaDocument,
    InputMediaPhoto,
    InputMediaVideo,
    InputMediaAudio,
)
from helper import db, module, prefix, exception_str


def get_filters_chat(chat_id):
    return db.get(f"{chat_id}", {})


def set_filters_chat(chat_id, filters_):
    return db.set(f"{chat_id}", filters_)


async def contains_filter(_, __, m):
    return m.text and m.text.lower() in get_filters_chat(m.chat.id).keys()


contains = filters.create(contains_filter)


@module(contains)
async def filters_main_handler(client: Client, message: Message):
    value = get_filters_chat(message.chat.id)[message.text.lower()]
    try:
        await client.get_messages(int(value["CHAT_ID"]), int(value["MESSAGE_ID"]))
    except errors.RPCError:
        raise ContinuePropagation

    if value.get("MEDIA_GROUP"):
        messages_grouped = await client.get_media_group(
            int(value["CHAT_ID"]), int(value["MESSAGE_ID"])
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
                        InputMediaVideo(_.video.file_id, _.video.thumbs[0].file_id)
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
                            InputMediaDocument(_.document.file_id, _.caption.markdown)
                        )
                elif _.document.thumbs:
                    media_grouped_list.append(
                        InputMediaDocument(
                            _.document.file_id, _.document.thumbs[0].file_id
                        )
                    )
                else:
                    media_grouped_list.append(InputMediaDocument(_.document.file_id))
        await client.send_media_group(
            message.chat.id,
            media_grouped_list,
            reply_to_message_id=message.id,
        )
    else:
        await client.copy_message(
            message.chat.id,
            int(value["CHAT_ID"]),
            int(value["MESSAGE_ID"]),
            reply_to_message_id=message.id,
        )
    raise ContinuePropagation


@module(
    cmds="filter", args=["название"], desc="Создать триггер в чате (Обязательно реплай)"
)
async def filter_handler(client: Client, message: Message):
    try:
        if len(message.text.split()) < 2:
            return await message.edit(
                f"<b>🔨 Использование</b>: <code>{prefix()}filter [название] (Обязательно реплай)</code>"
            )
        name = message.text.split(maxsplit=1)[1].lower()
        chat_filters = get_filters_chat(message.chat.id)
        if name in chat_filters.keys():
            return await message.edit(
                f"<b>🥧 Фильтр</b> <code>{name}</code> уже существует."
            )
        if not message.reply_to_message:
            return await message.edit(
                "<b>🥧 Ответьте на сообщение</b> пожалуйста. (реплай)"
            )

        try:
            chat = await client.get_chat(db.get("chat_id", 0))
        except (errors.RPCError, ValueError, KeyError):
            chat = await client.create_supergroup(
                "🧛‍♂️ lordnet-userbot Фильтры",
                "Не трогайте этот чат пожалуйста и не удаляйте его!",
            )
            db.set("chat_id", chat.id)

        chat_id = chat.id

        if message.reply_to_message.media_group_id:
            get_media_group = [
                _.id
                for _ in await client.get_media_group(
                    message.chat.id, message.reply_to_message.id
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
            filter_ = {
                "MESSAGE_ID": str(message_id[1].id),
                "MEDIA_GROUP": True,
                "CHAT_ID": str(chat_id),
            }
        else:
            try:
                message_id = await message.reply_to_message.forward(chat_id)
            except errors.ChatForwardsRestricted:
                if message.reply_to_message.text:
                    # manual copy
                    message_id = await client.send_message(
                        chat_id, message.reply_to_message.text
                    )
                else:
                    await message.edit(
                        "<b>⛔ Пересылка сообщений запрещена админами чата</b>"
                    )
                    return
            filter_ = {
                "MEDIA_GROUP": False,
                "MESSAGE_ID": str(message_id.id),
                "CHAT_ID": str(chat_id),
            }

        chat_filters.update({name: filter_})

        set_filters_chat(message.chat.id, chat_filters)
        return await message.edit(
            f"<b>🥧 Фильтр</b> <code>{name}</code> создан успешно."
        )
    except Exception as e:
        return await message.edit(exception_str(e))


@module(cmds="filters", desc="Список фильтров в чате")
async def filters_handler(_: Client, message: Message):
    try:
        text = ""
        for index, a in enumerate(get_filters_chat(message.chat.id).items(), start=1):
            key, item = a
            key = key.replace("<", "").replace(">", "")
            text += f"{index}. <code>{key}</code>\n"
        text = f"<b>🥧 Ваши фильтры в этом чате</b>:\n\n" f"{text}"
        text = text[:4096]
        return await message.edit(text)
    except Exception as e:
        return await message.edit(exception_str(e))


@module(
    cmds=["delfilter", "filterdel", "fdel"], args=["название"], desc="Удалить фильтр"
)
async def filter_del_handler(_: Client, message: Message):
    try:
        if len(message.text.split()) < 2:
            return await message.edit(
                f"<b>🥧 Используйте</b>: <code>{prefix()}fdel [название]</code>"
            )
        name = message.text.split(maxsplit=1)[1].lower()
        chat_filters = get_filters_chat(message.chat.id)
        if name not in chat_filters.keys():
            return await message.edit(
                f"<b>🥧 Фильтра</b> <code>{name}</code> не существует."
            )
        del chat_filters[name]
        set_filters_chat(message.chat.id, chat_filters)
        return await message.edit(
            f"<b>🥧 Фильтр</b> <code>{name}</code> был удалён успешно."
        )
    except Exception as e:
        return await message.edit(exception_str(e))


@module(cmds="fsearch", args=["название"], desc="Информация о фильтре")
async def filter_search_handler(_: Client, message: Message):
    try:
        if len(message.text.split()) < 2:
            return await message.edit(
                f"<b>🥧 Используйте</b>: <code>{prefix}fsearch [название]</code>"
            )
        name = message.text.split(maxsplit=1)[1].lower()
        chat_filters = get_filters_chat(message.chat.id)
        if name not in chat_filters.keys():
            return await message.edit(
                f"<b>🥧 Фильтра</b> <code>{name}</code> не существует."
            )
        return await message.edit(
            f"<b>🥧 Фильтр</b>:\n<code>{name}</code"
            f">\n<b>😋 Ответ</b>:\n{chat_filters[name]}"
        )
    except Exception as e:
        return await message.edit(exception_str(e))
