from asyncio import sleep

from helper import module, Message, Client


@module(cmds="del", desc="Delete message")
async def del_msg(client: Client, message: Message):
    if message.reply_to_message:
        await client.delete_messages(
            message.chat.id, [message.message_id, message.reply_to_message.message_id]
        )
    else:
        try:
            await client.delete_messages(
                message.chat.id, [message.message_id, message.message_id - 1]
            )
        except:
            pass


@module(cmds="purge", args=["count"], desc="Purge messages")
async def purge(client: Client, message: Message):
    try:
        count = int(message.command[1])
    except IndexError:
        count = 0
    chunk = []
    async for msg in client.iter_history(
        chat_id=message.chat.id,
        offset_id=message.reply_to_message.message_id
        if message.reply_to_message
        else None,
        reverse=not bool(count),
        limit=count,
    ):
        chunk.append(msg.message_id)
        if len(chunk) >= 100:
            await client.delete_messages(message.chat.id, chunk)
            chunk = []
            await sleep(1)

    if len(chunk) > 0:
        await client.delete_messages(message.chat.id, chunk)
