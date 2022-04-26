# Инструкция к созданию модуля

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
![GitHub last commit](https://img.shields.io/github/last-commit/LORD-ME-CODE/lordnet-userbot)

[@lordnet_userbot](https://t.me/lordnet_userbot)

```python
from helper import module, Message
from helper import Client  # Вы можете импортировать клиент
from helper import db  # Вы можете импортировать базу данных
from helper import session  # Вы можете импортировать ClientSession

from helper import import_library, aimport_library  # Example 4
from helper import exception_str  # Example 5


# Функция может быть как и sync, так и async
# commands принимает список команд или же одну команду
# args принимает список аргументов в которых нуждается команд(ы) модуля
# desc принимает описание модуля (форматирование html)
@module(commands="example", args=["text"], description="Пример модуля")
async def example(_, message: Message):
    text = message.text.split(maxsplit=1)[1]
    await message.edit("Привет, я модуль example!\n" f"{text}")


from pyrogram import filters


# * принимает фильтры пирограма, тоесть можно юзать кастомные
@module(filters.me & filters.group)
async def example(_, message: Message):
    text = message.text
    await message.reply("Привет, я модуль example2!\n" f"{text}")


# Пример использования базы данных
@module(commands="example3", args=["text"], desc="Пример базы данных")
async def example(_, message: Message):
    text = message.text.split(maxsplit=1)[1]
    db.set(f"value", text)  # Устанавливаем значение value на text который ввёл юзер

    value = db.get("value")  # Получаем значение из базы данных
    values = db.get_collection()  # Получаем все значения из базы данных

    db.remove("value")  # Удаляем значение из базы данных


# Пример использования импорта с установкой
example5 = import_library("example5")  # Импортируем модуль example5
flask_cors = import_library(
    "flask_cors", "flask-cors"
)  # Импорт с необычным названием пакета PYPI


@module(commands="example4", description="Пример импорта с установкой")
async def example(_, message: Message):
    text = message.text.split(maxsplit=1)[1]
    aiohttp = await aimport_library("aiohttp")  # Импортируем модуль асинхронно
    # Используйте асинк импорт модуль чтобы не было зависаний в юзерботе при загрузке вашего модуля

        
made_by = "@lord_code"  # Можно указать автора модуля (не обязательно)
```
