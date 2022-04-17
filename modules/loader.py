import os
from io import BytesIO

from helper import (
    module,
    Message,
    modules_dict,
    prefix,
    module_exists,
    session,
    load_module,
    restart,
)
from validators import url

# noinspection PyShadowingBuiltins
from aiofile import async_open as open

from helper.misc import lordnet_url


@module(
    cmds=["load", "unload", "lm", "um", "updatemod"],
    desc="Load/unload modules",
    args=["name/link"],
)
async def loader_cmd(_, message: Message):
    cmd = message.command[0]
    if cmd in ["load", "lm"]:
        if len(message.command) == 1 and not (
            message.reply_to_message
            and not message.reply_to_message.document
            and not message.reply_to_message.document.file_name.casefold().endswith(
                ".py"
            )
        ):
            await message.edit("<b>🙄 Please specify a module to load</b>")
            return
        if message.reply_to_message:
            name = message.reply_to_message.document.file_name.split(".")[0]
            is_url = False
            is_file = True
        else:
            is_file = False
            name = message.command[1].lower()
            if url(name):
                name = name.split("/")[-1].replace(".py", "")
                is_url = True
            else:
                is_url = False
        if modules_dict.module_in(name):
            await message.edit(
                f"<b>🙄 Module <code>{name}</code> already loaded\n"
                f"🔃 Type <code>{prefix()}updatemod {name}</code> to update it</b>"
            )
            return

        if not is_url and not is_file:
            if not await module_exists(name):
                await message.edit(f"<b>🙄 Module <code>{name}</code> does not exist\n")
                return
        elif is_file:
            await message.reply_to_message.download("custom/" + name + ".py")
            await load_module(name + ".py")
        else:
            link = message.command[1]
            async with session.get(link) as response:
                if response.status != 200:
                    await message.edit(
                        f"<b>🙄 Module <code>{name}</code> does not exist\n"
                        f"🔃 Check the link and try again</b>"
                    )
                    return
                data = await response.read()
                if b"@module" not in data or b"from helper import" not in data:
                    return await message.edit(
                        f"<b>🙄 Module <code>{name}</code> is not a valid module\n"
                        f"🔃 Check it and try again</b>"
                    )
                async with open(f"custom/{name}.py", "wb") as f:
                    await f.write(data)
                await load_module(name + ".py")
        await message.edit(f"<b>💪 Module <code>{name}</code> loaded</b>")
    elif cmd == "updatemod":
        if len(message.command) == 1:
            await message.edit("<b>🙄 Please specify a module to update</b>")
            return
        name = message.command[1].lower()
        if url(name):
            name = message.command[1].split("/")[-1].replace(".py", "")
            is_url = True
        else:
            is_url = False
        if not modules_dict.module_in(name):
            await message.edit(
                f"<b>🙄 Module <code>{name}</code> not loaded\n"
                f"🔃 Type <code>{prefix()}lm {message.command[1].lower()}</code> to load it</b>"
            )
            return
        if not is_url:
            link = lordnet_url + f"modules/{name}.py"
        else:
            link = message.command[1]
        async with session.get(link) as response:
            if response.status != 200:
                await message.edit(
                    f"<b>🙄 Module <code>{name}</code> does not exist\n"
                    f"🔃 Check the link and try again</b>"
                )
                return
            data = await response.read()
            if is_url and (b"@module" not in data or b"from helper import" not in data):
                return await message.edit(
                    f"<b>🙄 Module <code>{name}</code> is not a valid module\n"
                    f"🔃 Check the link and try again</b>"
                )
            async with open(f"custom/{name}.py", "wb") as f:
                await f.write(data)
            await load_module(name + ".py")
    else:
        if len(message.command) == 1:
            await message.edit("<b>🙄 Please specify a module to unload</b>")
            return
        name = message.command[1].split("/")[-1].replace(".py", "")
        if name + ".py" not in os.listdir("custom"):
            await message.edit(f"<b>🙂 Module <code>{name}</code> not found.</b>")
            return
        os.remove(f"custom/{name}.py")
        await message.edit(f"<b>💪 Module <code>{name}</code> unloaded</b>")
        restart()


@module(cmds=["loadall", "unloadall"], desc="(Un)Load all modules")
async def load_all(_, message: Message):
    if message.command[0] == "loadall":
        #  pass
        await message.edit("<b>💪 All modules loaded</b>")
    else:
        for name in os.listdir("custom"):
            os.remove(f"custom/{name}")
        await message.edit("<b>💪 All modules unloaded</b>")
    restart()


@module(cmds=["bm", "backupmod"], args=["name"], desc="Backup a module")
async def backup_module(_, message: Message):
    if len(message.command) == 1:
        await message.edit("<b>🙄 Please specify a module to backup</b>")
        return
    name = message.command[1].split("/")[-1].replace(".py", "")
    if name + ".py" not in os.listdir("custom"):
        await message.edit(f"<b>🙂 Module <code>{name}</code> not found.</b>")
        return
    await message.delete()
    async with open(f"custom/{name}.py", "rb") as f:
        data = BytesIO(await f.read())
        data.name = f"{name}.py"
        data.seek(0)
        await message.reply_document(
            data,
            caption=f"<b>💪 Module <code>{name}</code> backed up</b>",
        )
