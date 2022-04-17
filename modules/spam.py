from asyncio import sleep

from helper import module, Message, prefix


cooldowns = {"spam": 0.15, "fastspam": 0}


@module(commands=["spam", "fastspam"], args=["кол-во", "текст"])
async def spam_cmd(_, message: Message):
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
    reply = message.reply_to_message.message_id if message.reply_to_message else None

    if cooldown:
        for _ in range(int(message.command[1])):
            await message.reply(text=text, reply_to_message_id=reply)
            await sleep(cooldown)
    else:
        for _ in range(int(message.command[1])):
            await message.reply(text=text, reply_to_message_id=reply)
