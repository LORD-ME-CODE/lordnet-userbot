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
    messages = [
        msg
        async for msg in client.get_chat_history(
            chat_id=message.chat.id,
            offset_id=message.reply_to_message.id if message.reply_to_message else None,
            limit=count,
        )
    ]
    if not bool(count):
        messages = messages[::-1]
    for msg in messages:
        chunk.append(msg.id)
        if len(chunk) >= 100:
            await client.delete_messages(message.chat.id, chunk)
            chunk = []
            await sleep(1)

    if len(chunk) > 0:
        await client.delete_messages(message.chat.id, chunk)
