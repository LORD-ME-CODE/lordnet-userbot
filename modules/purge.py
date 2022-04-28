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

from asyncio import sleep

from helper import module, Message, Client


@module(cmds="del", desc="Удалить сообщение (ответ или удалится сообщение выше)")
async def del_msg(client: Client, message: Message):
    if message.reply_to_message:
        await client.delete_messages(
            message.chat.id, [message.id, message.reply_to_message.id]
        )
    else:
        try:
            await client.delete_messages(message.chat.id, [message.id, message.id - 1])
        except:
            pass


@module(cmds="purge", args=["кол-во"], desc="Массовое удаление сообщений")
async def purge(client: Client, message: Message):
    try:
        count = int(message.command[1])
    except IndexError:
        count = 0
    chunk = []
    async for msg in client.get_chat_history(
        chat_id=message.chat.id,
        offset_id=message.reply_to_message_id,
        limit=count,
    ):
        chunk.append(msg.id)
        if len(chunk) >= 100:
            await client.delete_messages(message.chat.id, chunk)
            chunk = []
            await sleep(1)

    if len(chunk) > 0:
        await client.delete_messages(message.chat.id, chunk)
