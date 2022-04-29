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

if __name__ == "__main__":
    import sys
    import logging
    import os
    from threading import Timer

    from pyrogram import Client
    from pyrogram.enums import ParseMode
    from pyrogram.errors import RPCError, SessionPasswordNeeded
    from pyrogram.types import SentCode

    import config
    from flask import Flask, render_template, request

    install_type = sys.argv[1] if len(sys.argv) > 1 else "3"
    if install_type == "1":
        restart = "pm2 restart lordnet"
    elif install_type == "2":
        restart = "sudo systemctl restart lordnet"
    else:
        restart = "cd lordnet-userbot/ && python run.py"

    app = Flask(__name__, template_folder="web", static_folder="docs/assets")

    @app.route("/favicon.ico")
    def favicon():
        return app.send_static_file("lordnet.ico")

    @app.route("/", methods=["POST", "GET"])
    def index():
        return render_template(
            "install.html", api_id=config.api_id, api_hash=config.api_hash
        )

    phone: str
    api_id: str
    api_hash: str
    password: str
    sent_code: SentCode
    client: Client

    already: bool = False

    @app.route("/sms", methods=["POST"])
    def sms_handler():
        global client, phone, api_id, api_hash, password, already
        data = request.form
        phone = data.get("phone")
        api_id = data.get("api_id")
        api_hash = data.get("api_hash")
        password = data.get("password")
        if phone and api_id and api_hash:
            client = Client(
                "lordnet",
                api_id=api_id,
                api_hash=api_hash,
                hide_password=True,
                parse_mode=ParseMode.HTML,
            )
            try:
                if not already:
                    global sent_code
                    client.connect()
                    sent_code = client.send_code(phone)
                    already = True
                with open(".env", "w") as f:
                    f.write(f"API_ID = {api_id}\nAPI_HASH = {api_hash}")
                return render_template("sms.html", phone=phone)
            except Exception as ex:
                return f"<pre>{ex}</pre>"

    @app.route("/code", methods=["POST"])
    def code_handler():
        code = request.form.get("code")
        try:
            signed_id = client.sign_in(phone, sent_code.phone_code_hash, code)
        except SessionPasswordNeeded:
            try:
                signed_id = client.check_password(password)
                if not signed_id:
                    raise Exception("Not signed in")
            except Exception as ex:
                return f"<pre>{ex}</pre>"
        except Exception as ex:
            return f"<pre>{ex}</pre>"

        client.disconnect()

        if not signed_id:
            return f"<pre>Not signed in</pre>"
        else:
            client.start()
            # noinspection PyPep8
            try:
                text = (
                    '<b><a href="https://t.me/lordnet_userbot">✉ lordnet-userbot</a> download success:\n\n'
                    f"🎲 Модули: @lordnet_modules\n"
                    f"📃 Лицензия: <a href='https://github.com/LORD-ME-CODE/lordnet-userbot/blob/main/LICENSE'>"
                    f"GNU v3.0</a>\n"
                    f"☛ Репо: <a href='https://github.com/LORD-ME-CODE/lordnet-userbot'>lordnet-userbot</a>\n\n"
                    f"☛ Канал: @lordnet_userbot\n"
                    f"☛ Чат: @lordnetchat\n"
                    f"☛ Кодер: @lord_code</b>\n"
                    f"☛ Используйте для старта:\n<code>{restart}</code></b>"
                )
                client.send_message("me", text.format(restart))
                try:
                    client.join_chat("lordnet_userbot")
                    client.join_chat("lordnetchat")
                except RPCError:
                    pass
            except RPCError:
                pass

            client.stop()

            Timer(1.25, lambda: os._exit(0)).start()

            return (
                "<h2>Успешный вход! Можете вернуться в консоль!</h2><br><br>"
                "Команда для запуска юзербота: <code>{}</code>".format(restart)
            )

    @app.errorhandler(500)
    def error_handler(e):
        return (
            "<h2>Если вы ввели верный код, то зайдите в консоль и нажмите</h2><br>"
            "<code>CTRL + C</code><br>А потом напишите<br><code>{}</code>".format(
                restart
            ),
            200,
        )

    print("[+] Запускаю lordnet web...\n")

    def main():
        import socket

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("10.255.255.255", 1))
            host = s.getsockname()[0]
        except Exception:
            try:
                host = socket.gethostbyname(socket.gethostname())
            except Exception:
                try:
                    host = socket.gethostbyname(socket.getfqdn())
                except Exception:
                    host = "localhost"
        host += ":5000"
        print(
            "\n"
            "[!] Успешно запущен lordnet web!\n"
            f"[!] Для продолжения установки\n"
            f"[+] Перейдите по ссылке: http://{host}"
            f"\n"
        )
        try:
            import webbrowser

            webbrowser.open(host)
        except Exception:
            pass

    Timer(1.25, main).start()

    log = logging.getLogger("werkzeug")
    log.setLevel(logging.ERROR)

    try:
        app.run(debug=False, port=5000, host="0.0.0.0")
    except RuntimeError:
        sys.exit(3)
