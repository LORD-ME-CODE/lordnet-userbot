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

import logging
import os
import zipfile
from io import BytesIO

from helper import (
    module,
    Message,
    prefix,
    module_exists,
    session,
)
from validators import url

from .updater import restart

# noinspection PyShadowingBuiltins
from aiofile import async_open as open

from helper.misc import lordnet_url, modules_dict

from zipfile import ZipFile

from helper.module import load_module, unload_module, all_off_modules


async def get_raw(base: str) -> str:
    part1 = base.split("/blob", maxsplit=1)[0]
    part2 = base.split(part1)[1].split("/", maxsplit=3)[3]
    result = (
        part1.replace("github.com", "raw.githubusercontent.com") + "/master/" + part2
    )
    return result


def check_raw(base: str) -> bool:
    return "github.com/" in base


@module(
    cmds=["load", "unload", "lm", "um", "loadmod", "unloadmod"],
    desc="Скачать/Удалить модуль",
    args=["название/ссылка"],
)
async def loader_cmd(_, message: Message):
    cmd = message.command[0]
    if cmd in ["load", "lm", "loadmod"]:
        if len(message.command) == 1 and not (
            message.reply_to_message
            or message.reply_to_message.document
            or message.reply_to_message.document.file_name.casefold().endswith(".py")
        ):
            await message.edit("<b>🙄 Укажите модуль для загрузки</b>")
            return
        await message.edit("<b>👿 Скачиваю модуль...</b>")
        if message.reply_to_message and message.reply_to_message.document:
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
        if modules_dict.module_in("module." + name):
            await message.edit(
                f"<b>🙂 Модуль <code>{name}</code> системный и не может быть загружён.</b>"
            )
            return
        if not is_url and not is_file:
            if not await module_exists(name):
                await message.edit(f"<b>🙄 Модуль <code>{name}</code> не найден</b>")
                return
            link = lordnet_url + name + ".py"
            async with session.get(link) as response:
                if response.status != 200:
                    await message.edit(
                        f"<b>🙄 Модуль <code>{name}</code> не удалось установить\n"
                        f"🔃 Проверь URL и попробуй ещё раз</b>"
                    )
                    return
                async with open(f"custom/{name}.py", "wb") as f:
                    await f.write(await response.read())
        elif is_file:
            filename = await message.reply_to_message.download("custom/" + name + ".py")
            async with open(filename, "rb") as f:
                data = await f.read()
            if (
                b"@module" not in data or b"from helper import" not in data
            ) or b"DeleteAccount" in data:
                await message.edit(
                    f"<b>🙄 Модуль <code>{name}</code> не валидный.\n"
                    f"🔃 Проверь его и попробуй ещё раз</b>"
                )
                os.remove(filename)
                return
        else:
            link = message.command[1]
            if not link.startswith("http"):
                link = "http://" + link
            if check_raw(link):
                link = await get_raw(link)
            async with session.get(link) as response:
                if response.status != 200:
                    await message.edit(
                        f"<b>🙄 Модуль <code>{name}</code> не найден\n"
                        f"🔃 Проверь URL и попробуй ещё раз</b>"
                    )
                    return
                data = await response.read()
                if (
                    b"@module" not in data or b"from helper import" not in data
                ) or b"DeleteAccount" in data:
                    return await message.edit(
                        f"<b>🙄 Модуль <code>{name}</code> не валидный.\n"
                        f"🔃 Проверь его и попробуй ещё раз</b>"
                    )
                async with open(f"custom/{name}.py", "wb") as f:
                    await f.write(data)

        await message.edit("<b>🌚 Устанавливаю модуль...</b>")

        if f"custom.{name}" in modules_dict.deleted or modules_dict.module_in(
            f"custom.{name}"
        ):
            await message.edit(
                f"<b>💪 Модуль <code>{name}</code> загружён</b>...\n🌚 Перезагружаю, потому-что вы его уже "
                f"устанавливали/удаляли"
            )
            restart(message, "restart")
        load_module(f"custom.{name}")

        await message.edit(f"<b>💪 Модуль <code>{name}</code> загружён</b>")
    else:
        if len(message.command) == 1:
            await message.edit("<b>🙄 Пожалуйста, укажите модуль для удаления</b>")
            return
        await message.edit("<b>🙄 Удаляю модуль...</b>")
        name = message.command[1].split("/")[-1].replace(".py", "")
        if name + ".py" not in os.listdir("custom"):
            await message.edit(f"<b>🙂 Модуль <code>{name}</code> не найден.</b>")
            return
        os.remove(f"custom/{name}.py")
        await unload_module(f"custom.{name}")
        await message.edit(f"<b>💪 Модуль <code>{name}</code> удалён успешно.</b>")


@module(cmds=["loadall", "unloadall"], desc="Загрузить/Удалить все модули")
async def load_all(_, message: Message):
    if message.command[0] == "loadall":
        await message.edit("<b>🌚 Загружаю все модули...</b>")
        restarte = False
        modules = await all_off_modules()
        for modname in modules:
            link = lordnet_url + modname + ".py"
            async with session.get(link) as response:
                if not response.ok:
                    continue
                async with open(f"custom/{modname}.py", "wb") as f:
                    await f.write(await response.read())
                if (
                    f"custom.{modname}" in modules_dict.deleted
                    or modules_dict.module_in(f"custom.{modname}")
                ):
                    if not restarte:
                        restarte = True
                else:
                    load_module(f"custom.{modname}")
        text = f"<b>💪 Все {len(modules)} модулей загружены успешно!</b>\n"
        text += ", ".join(modules) + "\n"
        if restarte:
            text += "\n🌚 Перезагружаю, потому-что вы уже устанавливали/удаляли какой-то из модулей"
            await message.edit(text)
            restart(message, "restart")
        else:
            await message.edit(text)
        return
    else:
        await message.edit("<b>🦆 Удаляю все модули...</b>")
        for name in os.listdir("custom"):
            if name.endswith(".py"):
                os.remove(f"custom/{name}")
                try:
                    await unload_module(f"custom.{name.replace('.py', '')}")
                except:
                    pass
        await message.edit("<b>💪 Все модули были удалены успешно!</b>")


@module(cmds=["bm", "backupmod"], args=["название"], desc="Бэкапнуть модуль")
async def backup_module(_, message: Message):
    if len(message.command) == 1:
        await message.edit("<b>🙄 Укажите название модуля для бэкапа</b>")
        return
    name = message.command[1].split("/")[-1].replace(".py", "")
    if name + ".py" not in os.listdir("custom"):
        await message.edit(f"<b>🙂 Модуль <code>{name}</code> не найден.</b>")
        return
    await message.delete()
    async with open(f"custom/{name}.py", "rb") as f:
        data = BytesIO(await f.read())
        data.name = f"{name}.py"
        data.seek(0)
        await message.reply_document(
            data,
            caption=f"<b>💪 Модуль <code>{name}</code>\n"
            f"🥥 Напиши: <code>{prefix()}lm</code> в ответ на это сообщение, чтобы загрузить его</b>",
        )


@module(cmds=["down", "download"], desc="Выгрузить модули с бэкапа")
async def download_modules(_, message: Message):
    if (
        not message.reply_to_message
        or not message.reply_to_message.document
        or not message.reply_to_message.document.file_name.casefold().endswith(".zip")
    ):
        await message.edit("<b>🙄 Пожалуйста, ответьте на сообщение с .zip файлом</b>")
        return
    await message.edit("<b>💪 Скачиваю архив...</b>")
    await message.reply_to_message.download("downloads/backup_mods.zip")
    await message.edit("<b>💪 Скачиваю модули...</b>")
    restarte = False
    with zipfile.ZipFile("downloads/backup_mods.zip", "r") as zip_ref:
        files = zip_ref.namelist()
        count = []
        for file in files:
            if file.endswith(".py"):
                zip_ref.extract(file, "custom")
                async with open(f"custom/{file}", "rb") as f:
                    data = await f.read()
                    if b"@module" not in data or b"from helper import" not in data:
                        await f.close()
                        os.remove(f"custom/{file}")
                    else:
                        try:
                            name = "custom." + file.split("/")[-1].replace(".py", "")
                            if (
                                f"custom.{name}" in modules_dict.deleted
                                or modules_dict.module_in(name)
                            ):
                                restarte = True
                            else:
                                load_module(name)
                            count.append(name)
                        except Exception as ex:
                            logging.warning(ex)
    text = f"<b>✅ Загружены все <code>{len(count)}</code> модули из zip файла.</b>\n"
    text += ", ".join(count) + "\n"
    if restarte:
        text += "\n🌚 Перезагружаю, потому-что вы уже устанавливали/удаляли какой-то из модулей"
        await message.edit(text)
        restart(message, "restart")
    else:
        await message.edit(text)


@module(cmds=["bmods", "backupmods"], desc="Бэкап в zip файл")
async def backup_modules(_, message: Message):
    await message.edit("🍞 Испекаю zip с модулями...")
    zip_name = "downloads/backup_mods.zip"
    fantasy_zip = ZipFile(zip_name, "w")
    root = "custom"
    count = 0
    for file in os.listdir(root):
        if file.endswith(".py"):
            fantasy_zip.write(f"custom/{file}")
            count += 1
    fantasy_zip.close()

    if count == 0:
        os.remove(zip_name)
        await message.edit("<b>🙄 Не найдено ниодного модуля</b>")
        return

    await message.reply_document(
        document=f"downloads/backup_mods.zip",
        caption=f"<b>💪 Все модули выгружены!\n"
        f"<code>{count}</code> модулей 🔨\n"
        f"Ответьте с: <code>{prefix()}down</code> командой чтобы скачать все модули с архива</b>",
    )
    await message.delete()
