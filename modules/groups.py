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

import re
from contextlib import suppress
from datetime import datetime, timedelta
from typing import Any

from pyrogram import ContinuePropagation, filters
from pyrogram.enums import MessageEntityType, ChatMembersFilter, ChatMemberStatus
from pyrogram.errors import UserAdminInvalid, ChatAdminRequired, RPCError
from pyrogram.types import ChatPermissions, ChatPrivileges, ChatMember

from helper import module, Message, db, Client, escape_html, import_library
from time import time as unixtime_1


def unixtime() -> int:
    return int(unixtime_1())


class MyUser:
    def __init__(self, user: Any):
        self.user = user
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

    @property
    def last_name(self):
        return escape_html(self.user.last_name)


db_cache: dict = db.get_collection()


def update_cache():
    db_cache.clear()
    db_cache.update(db.get_collection())


def user_is_tmuted(chat_id: int, user_id: int) -> bool:
    return user_id in db_cache.get(f"{chat_id}_tmutes", [])


async def find_user_in_message(
    client: Client, message: Message, chat_member: bool = False
):
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
            if ms.type == MessageEntityType.TEXT_MENTION:
                user = ms.user
                text = message.text[ms.offset + 1 :]
                break
            elif ms.type == MessageEntityType.MENTION:
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
        if user is None:
            await message.edit(
                "<b>🧭 Не удалось найти пользователя в вашем сообщении</b>"
            )
            raise ContinuePropagation
    elif len(args) > 1 and args[1].isdigit():
        user = await client.get_users(int(args[1]))
        try:
            text = message.text.split(args[1], maxsplit=1)[1]
        except:
            text = ""
    else:
        await message.edit("<b>🧭 Не удалось найти пользователя в вашем сообщении</b>")
        raise ContinuePropagation
    if chat_member:
        return await message.chat.get_member(user.id)
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


langdetect = import_library("langdetect")
detect, DetectorFactory = langdetect.detect, langdetect.DetectorFactory


@module(
    cmds="antiarab",
    desc="Анти-араб в чате (вкл/выкл)",
)
async def antiarab_cmd(_: Client, message: Message):
    now = not db_cache.get(f"antiarab{message.chat.id}", False)
    db_cache[f"antiarab{message.chat.id}"] = now
    db.set(f"antiarab{message.chat.id}", now)
    return await message.edit(
        "<b>🧕 Вы успешно выключили Анти-араб в чате</b>"
        if not now
        else "<b>🧕 Вы успешно включили Анти-араб в чате</b>"
    )


@module(
    cmds=["antich", "antichannel"],
    desc="Анти-каналы в чате (вкл/выкл)",
)
async def antichannel_cmd(_: Client, message: Message):
    now = not db_cache.get(f"antichannel{message.chat.id}", False)
    db_cache[f"antichannel{message.chat.id}"] = now
    db.set(f"antichannel{message.chat.id}", now)
    return await message.edit(
        "<b>🦎 Вы успешно выключили Анти-каналы в чате</b>"
        if not now
        else "<b>🦎 Вы успешно включили Анти-каналы в чате</b>"
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


@module(cmds="kickdel", desc="Кикнуть удаленные аккаунты с чата")
async def kickdel_cmd(_, message: Message):
    await message.edit("<b>[🔴] Кикаю удалённые аккаунты...</b>")
    # noinspection PyTypeChecker
    values = [
        await message.chat.ban_member(
            user.user.id, datetime.now() + timedelta(seconds=31)
        )
        async for user in message.chat.get_members()
        if user.user.is_deleted
    ]
    await message.edit(
        f"<b>[🔴] Вы успешно кикнули {len(values)} удаленных пользователей</b>"
    )


@module(cmds="kickleave", desc="Кикнуть вышедших с чата")
async def kickleave_cmd(_, message: Message):
    await message.edit("<b>[🟠] Кикаю вышедших пользователей...</b>")
    # noinspection PyTypeChecker
    values = [
        await message.chat.ban_member(
            user.user.id, datetime.now() + timedelta(seconds=31)
        )
        async for user in message.chat.get_members()
        if user.status == ChatMemberStatus.LEFT
    ]
    await message.edit(
        f"<b>[🟠] Вы успешно кикнули {len(values)} вышедших пользователей</b>"
    )


admins_p = [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]


@module(
    cmds="cinfo", desc="Показать чат информацию о пользователе", args=["reply/user"]
)
async def uinfo_cmd(client: Client, message: Message):
    user: ChatMember = await find_user_in_message(client, message, True)
    if user is None:
        return await message.edit("<b>[🔴] Не удалось найти пользователя</b>")
    data = str(
        (user.permissions if user.permissions else "Дефолтные")
        if user.status not in admins_p
        else user.privileges
    )
    try:
        data = "{" + data.split("_", maxsplit=1)[1].split(",", maxsplit=1)[1]
    except IndexError:
        pass
    muted_by = (
        " by:" + MyUser(user.restricted_by).mention + f" до {user.until_date}"
        if user.restricted_by
        else ": Нет"
    )
    text = (
        f"<b>👾 Чат инфо об {MyUser(user.user).mention}:\n"
        f"🤡 Замучен {muted_by}\n"
        f"🥝 Приглашён by: {MyUser(user.invited_by).mention if user.invited_by else 'Никто'}\n"
        f"📅 Зашёл в чат: {user.joined_date}\n"
        f"\n"
        f"🈸 Разрешения: <code>"
        f"{data}"
        f"</code>\n</b>"
    )
    await message.edit(text=text)


@module(filters.group & ~filters.me)
async def tmuted_handler(_, message: Message):
    if user_is_tmuted(
        message.chat.id,
        message.from_user.id if message.from_user else message.sender_chat.id,
    ):
        with suppress(RPCError):
            await message.delete()

    if db_cache.get(f"antichannel{message.chat.id}", False) and message.sender_chat:
        with suppress(RPCError):
            await message.delete()
            await message.chat.ban_member(message.sender_chat.id)
        return

    if db_cache.get(f"antiraid{message.chat.id}", False):
        with suppress(RPCError):
            await message.delete()
            if message.from_user:
                await message.chat.ban_member(message.from_user.id)
            elif message.sender_chat:
                await message.chat.ban_member(message.sender_chat.id)
        return

    if message.new_chat_members:
        if db_cache.get(f"antiarab{message.chat.id}", False):
            with suppress(RPCError):
                for user in message.new_chat_members:
                    DetectorFactory.seed = 0
                    if (
                        detect(user.first_name) == "ar"
                        or detect(str(user.last_name)) == "ar"
                    ):
                        with suppress(RPCError):
                            await message.chat.ban_member(user.id)
        else:
            welcome = db_cache.get(f"welcome{message.chat.id}", "off")
            if welcome != "off":
                await message.reply(
                    welcome,
                    disable_web_page_preview=True,
                )

    raise ContinuePropagation
