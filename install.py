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

    try:
        text = 'lordnet-userbot started successfully\n' \
               'Type: <code>{}</code> to reload it'
        app.send_message(
            'me', text.format(restart)
        )
    except:
        pass
    app.stop()
