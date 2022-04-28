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

from helper import module, Message, prefix, Client


cooldowns = {"spam": 0.15, "fastspam": 0, "fs": 0}


@module(commands=["spam", "fastspam", "fs"], args=["кол-во", "текст"])
async def spam_cmd(client: Client, message: Message):
    cmd = message.command[0]

    if len(message.command) < 3:
        await message.reply(
            "<b>🙂 Используйте:</b> <code>{}{}</code> <code>[кол-во] [текст]</code>".format(
                prefix(), cmd
            )
        )
        return

    await message.delete()

    cooldown = cooldowns[cmd]

    text = message.text.split(maxsplit=2)[2]
    reply = message.reply_to_message_id
    chat_id = message.chat.id

    if cooldown:
        for _ in range(int(message.command[1])):
            await client.send_message(
                chat_id=chat_id, text=text, reply_to_message_id=reply
            )
            await sleep(cooldown)
    else:
        for _ in range(int(message.command[1])):
            await client.send_message(
                chat_id=chat_id, text=text, reply_to_message_id=reply
            )
