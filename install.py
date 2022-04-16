import sys

from pyrogram import Client
import config
from helper import __version__, python_version, modules_dict


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

    try:
        text = (
            '<b><a href="https://t.me/lordnet_userbot">✉ lordnet-userbot</a> Started successfully!\n\n'
            f"☛ lordnet version: <code>{__version__}</code>\n\n"
            f"☛ Python version: <code>{python_version}</code>\n"
            f"☛ Modules count: <code>{len(modules_dict)}</code>\n"
            f"☛ License: <a href='https://github.com/LORD-ME-CODE/lordnet-userbot/blob/main/LICENSE'>GNU v3.0</a>\n"
            f"☛ Channel: @lordnet_userbot\n"
            f"☛ Chat: @lordnetchat\n"
            f"☛ Repository: <a href='https://github.com/LORD-ME-CODE/lordnet-userbot'>lordnet-userbot</a>\n"
            f"☛ Dev: @lord_code</b>\n\n"
            f"☛ Use this to restart the bot:\n<code>{restart}</code></b>"
        )
        app.send_message("me", text.format(restart))
    except:
        pass
    app.stop()
