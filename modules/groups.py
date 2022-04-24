import re
from contextlib import suppress
from datetime import datetime
from typing import Any

from pyrogram import ContinuePropagation, filters
from pyrogram.errors import UserAdminInvalid, ChatAdminRequired, RPCError
from pyrogram.types import ChatPermissions, ChatPrivileges

from helper import module, Message, db, Client, escape_html
from time import time as unixtime_1


def unixtime() -> int:
    return int(unixtime_1())


class MyUser:
    def __init__(self, user: Any):
        self.id: int = user.id
        self.username: str = user.username
        self.first_name: str = escape_html(user.first_name)
        self.mention = (
            f"@{user.username}"
            if user.username
            else user.mention
            if hasattr(user, "mention")
            else f"""<a href='{user.invite_link if user.invite_link else f"tg://openmessage?chat_id={user.id}"}'>
{user.first_name}</a>"""
        )


db_cache: dict = db.get_collection()


def update_cache():
    db_cache.clear()
    db_cache.update(db.get_collection())


def user_is_tmuted(chat_id: int, user_id: int) -> bool:
    return user_id in db_cache.get(f"{chat_id}_tmutes", [])


async def find_user_in_message(client: Client, message: Message):
    args = message.text.split()
    if message.reply_to_message and message.reply_to_message.from_user:
        user = message.reply_to_message.from_user
        text = message.text
    elif message.reply_to_message and message.reply_to_message.sender_chat:
        user = message.reply_to_message.sender_chat
        text = message.text
    elif message.mentioned or "@" in message.text:
        user = None
        text = message.text
        for ms in message.entities:
            if ms.type == "text_mention":
                user = ms.user
                text = message.text[ms.offset + 1 :]
                break
            elif ms.type == "mention":
                try:
                    user = await client.get_users(str(ms))
                except RPCError:
                    try:
                        user = await client.get_users(
                            message.text[ms.offset + 1 :].split()[0]
                        )
                    except RPCError:
                        await message.edit(
                            "<b>🧭 Не удалось найти пользователя в вашем сообщении</b>"
                        )
                        raise ContinuePropagation
                text = message.text.split(user.username, maxsplit=1)[1]
                break
    elif len(args) > 1 and args[1].isdigit():
        user = await client.get_users(int(args[1]))
        try:
            text = message.text.split(args[1], maxsplit=1)[1]
        except:
            text = ""
    else:
        await message.edit("<b>🧭 Не удалось найти пользователя в вашем сообщении</b>")
        raise ContinuePropagation
    return MyUser(user), text


mute_permissions = ChatPermissions(
    can_send_messages=False,
    can_send_media_messages=False,
    can_send_polls=False,
    can_send_other_messages=False,
    can_add_web_page_previews=False,
    can_change_info=False,
    can_invite_users=False,
    can_pin_messages=False,
)


class DefaultMatch:
    # noinspection PyMethodMayBeStatic
    def end(self):
        return 0


default_match = DefaultMatch()


async def get_args(query: str, pass_time: bool = False):
    if not pass_time:
        res = 0
        for character in "мчднmhdw":
            match = re.search(rf"(\d+|(\d+\.\d+)){character}", query)
            if match:
                if character in "мm":
                    res += int(
                        float(match.string[match.start() : match.end() - 1]) * 60 // 1
                    )
                if character in "hч":
                    res += int(
                        float(match.string[match.start() : match.end() - 1]) * 3600 // 1
                    )
                if character in "dд":
                    res += int(
                        float(match.string[match.start() : match.end() - 1])
                        * 86400
                        // 1
                    )
                if character in "wн":
                    res += int(
                        float(match.string[match.start() : match.end() - 1])
                        * 604800
                        // 1
                    )
            else:
                match = default_match
        try:
            return res, query[match.end() :]
        except IndexError:
            raise ContinuePropagation
    else:
        try:
            return query.split(maxsplit=1)[1]
        except IndexError:
            return ""


@module(
    cmds="mute",
    desc="Замьютить пользователя",
    args=["reply/user", "время(1н/1д/1ч/1м)", "причина"],
)
async def mute_cmd(client: Client, message: Message):
    user, text = await find_user_in_message(client, message)
    if (await message.chat.get_member(user.id)).status in ("creator", "administrator"):
        return await message.edit("<b>🙃 Нельзя замьютить администратора</b>")
    time, reason = await get_args(text)
    try:
        await message.chat.restrict_member(
            user.id, until_date=unixtime() + time, permissions=mute_permissions
        )
    except (UserAdminInvalid, ChatAdminRequired):
        await message.edit("<b>👽 У вас нет прав, вы фемка</b>")
    await message.edit(
        f"<b>🔇 Вы успешно замьютили пользователя {user.mention}</b>\n"
        f"<b>📅 Время блокировки:</b> <code>{time}</code>\n"
        f"<b>📝 Причина:</b>\n{reason}"
    )


null = datetime.fromtimestamp(0)


@module(
    cmds="unmute",
    desc="Размьютить пользователя",
    args=["reply/user"],
)
async def unmute_cmd(client: Client, message: Message):
    user, _ = await find_user_in_message(client, message)
    if (await message.chat.get_member(user.id)).status in ("creator", "administrator"):
        return await message.edit("<b>🙃 Нельзя размьютить администратора</b>")
    try:
        await message.chat.restrict_member(
            user.id, until_date=null, permissions=message.chat.permissions
        )
    except (UserAdminInvalid, ChatAdminRequired):
        await message.edit("<b>👽 У вас нет прав, вы фемка</b>")
    await message.edit(f"<b>🔈 Вы успешно размьютили пользователя {user.mention}</b>")


@module(
    cmds="ban",
    desc="Забанить пользователя",
    args=["reply/user", "время(1н/1д/1ч/1м)", "причина"],
)
async def ban_cmd(client: Client, message: Message):
    user, text = await find_user_in_message(client, message)
    if (await message.chat.get_member(user.id)).status in ("creator", "administrator"):
        return await message.edit("<b>🙃 Нельзя забанить администратора</b>")
    time, reason = await get_args(text)
    try:
        await message.chat.ban_member(user.id, until_date=unixtime() + time)
    except (UserAdminInvalid, ChatAdminRequired):
        await message.edit("<b>👽 У вас нет прав, вы фемка</b>")
    await message.edit(
        f"<b>🚫 Вы успешно забанили пользователя {user.mention}</b>\n"
        f"<b>📅 Время блокировки:</b> <code>{time}</code>\n"
        f"<b>📝 Причина:</b>\n{reason}"
    )


@module(
    cmds="unban",
    desc="Разбанить пользователя",
    args=["reply/user"],
)
async def unban_cmd(client: Client, message: Message):
    user, _ = await find_user_in_message(client, message)
    if (await message.chat.get_member(user.id)).status in ("creator", "administrator"):
        return await message.edit("<b>🙃 Нельзя разбанить администратора</b>")
    try:
        await message.chat.unban_member(user.id)
    except (UserAdminInvalid, ChatAdminRequired):
        await message.edit("<b>👽 У вас нет прав, вы фемка</b>")
    await message.edit(f"<b>🚫 Вы успешно разбанили пользователя {user.mention}</b>")


@module(
    cmds="kick",
    desc="Кикнуть пользователя",
    args=["reply/user", "причина"],
)
async def kick_cmd(client: Client, message: Message):
    user, text = await find_user_in_message(client, message)
    if (await message.chat.get_member(user.id)).status in ("creator", "administrator"):
        return await message.edit("<b>🙃 Нельзя кикнуть администратора</b>")
    reason = await get_args(text, True)
    try:
        await message.chat.ban_member(
            user.id, until_date=datetime.fromtimestamp(unixtime() + 31)
        )
    except (UserAdminInvalid, ChatAdminRequired):
        await message.edit("<b>👽 У вас нет прав, вы фемка</b>")
    await message.edit(
        f"<b>👢 Вы успешно кикнули пользователя {user.mention}</b>\n"
        f"<b>📝 Причина:</b>\n{reason}"
    )


@module(
    cmds="promote",
    desc="Выдать админку",
    args=["reply/user", "prefix"],
)
async def promote_cmd(client: Client, message: Message):
    user, text = await find_user_in_message(client, message)
    prefix = await get_args(text, True)
    try:
        await message.chat.promote_member(
            user.id,
            ChatPrivileges(
                can_delete_messages=True,
                can_restrict_members=True,
                can_invite_users=True,
                can_pin_messages=True,
            ),
        )
        if prefix:
            await client.set_administrator_title(
                message.chat.id,
                message.reply_to_message.from_user.id,
                prefix,
            )
    except (UserAdminInvalid, ChatAdminRequired):
        await message.edit("<b>👽 У вас нет прав, вы фемка</b>")

    await message.edit(
        f"<b>👮 Вы успешно выдали админку пользователю {user.mention}</b>\n"
        f"<b>📝 Префикс:</b>\n{prefix}"
    )


@module(
    cmds="demote",
    desc="Забрать админку",
    args=["reply/user"],
)
async def demote_cmd(client: Client, message: Message):
    user, _ = await find_user_in_message(client, message)
    try:
        await message.chat.promote_member(
            user.id, ChatPrivileges(can_manage_chat=False)
        )
    except (UserAdminInvalid, ChatAdminRequired):
        await message.edit("<b>👽 У вас нет прав, вы фемка</b>")
    await message.edit(
        f"<b>👮 Вы успешно забрали админку у пользователя {user.mention}</b>"
    )


@module(
    cmds="tmute",
    desc="Мут (удаление сообщений)",
    args=["reply/user", "причина"],
)
async def tmute_cmd(client: Client, message: Message):
    user, text = await find_user_in_message(client, message)
    reason = await get_args(text, True)

    if f"{message.chat.id}_tmutes" not in db_cache:
        db_cache[f"{message.chat.id}_tmutes"] = [user.id]
    elif user.id in db_cache[f"{message.chat.id}_tmutes"]:
        return await message.edit("<b>🤫 {user.mention} Уже замьючен..</b>")
    else:
        db_cache[f"{message.chat.id}_tmutes"].append(user.id)

    db.set(f"{message.chat.id}_tmutes", db_cache[f"{message.chat.id}_tmutes"])

    await message.edit(
        f"<b>🔇 Вы успешно заТмутили пользователя {user.mention}</b>\n"
        f"<b>📝 Причина:</b>\n{reason}"
    )


@module(
    cmds="untmute",
    desc="Размут tmute",
    args=["reply/user"],
)
async def untmute_cmd(client: Client, message: Message):
    user, _ = await find_user_in_message(client, message)

    if f"{message.chat.id}_tmutes" not in db_cache:
        return await message.edit("<b>🙃 Нет мутов в этом чате!</b>")
    elif user.id not in db_cache[f"{message.chat.id}_tmutes"]:
        return await message.edit("<b>🙃 Пользователь не замуТчен</b>")

    db_cache[f"{message.chat.id}_tmutes"].remove(user.id)
    db.set(f"{message.chat.id}_tmutes", db_cache[f"{message.chat.id}_tmutes"])

    await message.edit(f"<b>🔇 Вы успешно разТмутили пользователя {user.mention}</b>")


@module(
    cmds="tmutes",
    desc="Список пользователей в тмуте",
)
async def tmutes_list(_, message: Message):
    if f"{message.chat.id}_tmutes" not in db_cache:
        return await message.edit("<b>🙃 Нет мутов в этом чате!</b>")
    tmutes = db_cache[f"{message.chat.id}_tmutes"]
    text = "✨ Список Тмутов в этом чате:\n\n" + "\n".join(
        f"{index}. <a href='tg://user?id={uid}'>{uid}</a>"
        for index, uid in enumerate(tmutes, start=1)
    )
    await message.edit(text[:4096])


@module(
    cmds="antiraid",
    desc="Анти-рейд в чате (вкл/выкл)",
)
async def antiraid_cmd(_: Client, message: Message):
    now = not db_cache.get(f"antiraid{message.chat.id}", False)
    db_cache[f"antiraid{message.chat.id}"] = now
    db.set(f"antiraid{message.chat.id}", now)
    return await message.edit(
        "<b>🔇 Вы успешно выключили Анти-рейд в чате</b>"
        if not now
        else "<b>🔇 Вы успешно включили Анти-рейд в чате</b>"
    )


@module(
    cmds="welcome",
    desc="Включить/выключить приветствие",
    args=["текст/off"],
)
async def welcome_cmd(_: Client, message: Message):
    if len(message.command) == 1:
        text = "off"
    else:
        text = message.text.split(maxsplit=1)[1]
    db_cache[f"welcome{message.chat.id}"] = text
    db.set(f"welcome{message.chat.id}", text)
    return await message.edit(
        "<b>🔇 Вы успешно выключили приветствие</b>"
        if text == "off"
        else "<b>✅ Вы успешно включили приветствие</b>"
    )


@module(filters.group & ~filters.me)
async def tmuted_handler(_, message: Message):
    if user_is_tmuted(
        message.chat.id,
        message.from_user.id if message.from_user else message.sender_chat.id,
    ):
        with suppress(RPCError):
            await message.delete()

    if db_cache.get(f"antiraid{message.chat.id}", False):
        with suppress(RPCError):
            await message.delete()
            if message.from_user:
                await message.chat.ban_member(message.from_user.id)
            elif message.sender_chat:
                await message.chat.ban_member(message.sender_chat.id)

    if message.new_chat_members:
        welcome = db_cache.get(f"welcome{message.chat.id}", "off")
        if welcome != "off":
            await message.reply(
                welcome,
                disable_web_page_preview=True,
            )

    raise ContinuePropagation
