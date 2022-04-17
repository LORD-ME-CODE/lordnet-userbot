import os
import shutil
import zipfile
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

from zipfile import ZipFile


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
        if modules_dict.module_in("custom." + name) or modules_dict.module_in(
            "module." + name
        ):
            await message.edit(
                f"<b>🙄 Module <code>{name}</code> already loaded\n"
                f"🔃 Type <code>{prefix()}updatemod {name}</code> to update it</b>"
            )
            return

        if not is_url and not is_file:
            if not await module_exists(name):
                await message.edit(
                    f"<b>🙄 Module <code>{name}</code> does not exist</b>"
                )
                return
            link = lordnet_url + f"custom/{name}.py"
        elif is_file:
            await message.reply_to_message.download("custom/" + name + ".py")
            await load_module(name)
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
                await load_module(name)
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
        if not modules_dict.module_in("custom." + name):
            await message.edit(
                f"<b>🙄 Module <code>{name}</code> not loaded\n"
                f"🔃 Type <code>{prefix()}lm {message.command[1].lower()}</code> to load it</b>"
            )
            return
        if not is_url:
            if not await module_exists(name):
                await message.edit(
                    f"<b>🙄 Module <code>{name}</code> does not exist</b>"
                )
                return
            link = lordnet_url + f"custom/{name}.py"
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
            await load_module(name)
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


@module(cmds=["down", "download"], desc="Download module from zip file")
async def download_modules(_, message: Message):
    if (
        not message.reply_to_message
        or not message.reply_to_message.document
        or not message.reply_to_message.document.file_name.casefold().endswith(".zip")
    ):
        await message.edit("<b>🙄 Please reply to a zip file with modules</b>")
        return
    await message.edit("<b>💪 Downloading zip...</b>")
    await message.reply_to_message.download("downloads/backup_mods.zip")
    await message.edit("<b>💪 Downloading modules...</b>")
    with zipfile.ZipFile("downloads/backup_mods.zip", "r") as zip_ref:
        files = zip_ref.namelist()
        count = 0
        for file in files:
            if file.endswith(".py"):
                zip_ref.extract(file, "custom")
                async with open(f"custom/{file}", "rb") as f:
                    data = await f.read()
                    if b"@module" not in data or b"from helper import" not in data:
                        await f.close()
                        os.remove(f"custom/{file}")
                    else:
                        count += 1
    await message.edit(
        f"<b>✅ Downloaded all <code>{count}</code> modules from zip file.</b>"
    )
    restart()


@module(cmds=["bmods", "backupmods"], desc="Backup all modules")
async def backup_modules(_, message: Message):
    await message.delete()
    zip_name = "downloads/backup_mods.zip"
    fantasy_zip = ZipFile(zip_name, "w")
    root = "custom"
    count = 0
    for file in os.listdir(root):
        if file.endswith(".py"):
            fantasy_zip.write(file)
            count += 1
    fantasy_zip.close()

    if count == 0:
        os.remove(zip_name)
        await message.edit("<b>🙄 No modules found</b>")
        return

    await message.reply_document(
        document=f"downloads/backup_mods.zip",
        caption=f"<b>💪 All modules backed up\n"
        f"<code>{count}</code> modules 🔨\n"
        f"Reply with: <code>{prefix()}down</code> command to download this modules</b>",
    )
