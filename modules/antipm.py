from pyrogram import filters
from pyrogram.errors import RPCError
from pyrogram.raw import functions

from helper import module, Message, Client, db, answer


_data = db.get(
    "antipm",
    {
        "status": False,
        "report": False,
        "block": False,
    },
)


@module(
    cmds="antipm",
    desc="Включить анти-личку",
)
async def antipm_onoff(_: Client, message: Message):
    now = not _data["status"]
    _data["status"] = now
    db.set("antipm", _data)
    await answer(message, f"<b>🥰 Анти-личка {'включена' if now else 'выключена'}</b>")


@module(
    cmds=["pmrep", "pmreport"],
    desc="Включить авто-жалобы",
)
async def antipm_report(_: Client, message: Message):
    now = not _data["report"]
    _data["report"] = now
    db.set("antipm", _data)
    await answer(message, f"<b>🥰 Авто-Жалобы {'включены' if now else 'выключены'}</b>")


@module(
    cmds=["pmblock", "pmban"],
    desc="Включить авто-блокировку",
)
async def antipm_block(_: Client, message: Message):
    now = not _data["block"]
    _data["block"] = now
    db.set("antipm", _data)
    await answer(
        message, f"<b>🥰 Авто-блокировка {'включена' if now else 'выключена'}</b>"
    )


@module(
    filters.private
    & ~filters.me
    & ~filters.bot
    & ~filters.contact
    & ~filters.create(lambda _, __, m: m.chat.is_support)
    & filters.create(lambda _, __, ___: _data["status"])
)
async def anti_pm_handler(client: Client, message: Message):
    try:
        user_info = await client.resolve_peer(message.chat.id)
        if _data["report"]:
            await client.invoke(functions.messages.ReportSpam(peer=user_info))
        if _data["block"]:
            await client.invoke(functions.contacts.Block(id=user_info))
        await client.invoke(
            functions.messages.DeleteHistory(peer=user_info, max_id=0, revoke=True)
        )
    except RPCError:
        pass
