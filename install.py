import os.path
import sys

from pyrogram import Client
import config


if __name__ == "__main__":
    app = Client(
        "lordnet",
        api_id=config.api_id,
        api_hash=config.api_hash,
        hide_password=True,
    )

    install_type = sys.argv[1] if len(sys.argv) > 1 else "3"
    if install_type == "1":
        restart = "pm2 restart lordnet"
    elif install_type == "2":
        restart = "sudo systemctl restart lordnet"
    else:
        restart = "cd lordnet-userbot/ && python run.py"

    app.start()

    # noinspection PyPep8
    try:
        text = (
            '<b><a href="https://t.me/lordnet_userbot">✉ lordnet-userbot</a> download success!\n\n'
            f"☛ Лицензия: <a href='https://github.com/LORD-ME-CODE/lordnet-userbot/blob/main/LICENSE'>GNU v3.0</a>\n"
            f"☛ Канал: @lordnet_userbot\n"
            f"☛ Чат: @lordnetchat\n"
            f"☛ Репо: <a href='https://github.com/LORD-ME-CODE/lordnet-userbot'>lordnet-userbot</a>\n"
            f"☛ Кодер: @lord_code</b>\n\n"
            f"☛ Используйте для старта:\n<code>{restart}</code></b>"
        )
        app.send_message("me", text.format(restart))
    except:
        pass

    app.stop()
