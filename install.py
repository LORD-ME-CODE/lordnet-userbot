if __name__ == "__main__":
    import sys
    import logging
    from threading import Timer

    from pyrogram import Client
    from pyrogram.enums import ParseMode
    from pyrogram.errors import RPCError, SessionPasswordNeeded
    from pyrogram.types import SentCode

    import config
    from aioflask import Flask, render_template, request

    install_type = sys.argv[1] if len(sys.argv) > 1 else "3"
    if install_type == "1":
        restart = "pm2 restart lordnet"
    elif install_type == "2":
        restart = "sudo systemctl restart lordnet"
    else:
        restart = "cd lordnet-userbot/ && python run.py"

    app = Flask(__name__, template_folder="web")

    @app.route("/", methods=["POST", "GET"])
    async def index():
        return await render_template(
            "install.html", api_id=config.api_id, api_hash=config.api_hash
        )

    phone: str
    api_id: str
    api_hash: str
    password: str
    sent_code: SentCode
    client: Client

    @app.route("/sms", methods=["POST"])
    async def sms_handler():
        global client, phone, api_id, api_hash, password
        data = request.form
        phone = data.get("phone")
        api_id = data.get("api_id")
        api_hash = data.get("api_hash")
        password = data.get("password")
        if phone and api_id and api_hash:
            client = Client(
                "lordnet",
                api_id=config.api_id,
                api_hash=config.api_hash,
                hide_password=True,
                parse_mode=ParseMode.HTML,
            )
            try:
                global sent_code
                await client.connect()
                sent_code = await client.send_code(phone)
                return await render_template("sms.html", phone=phone)
            except Exception as ex:
                return f"<pre>{ex}</pre>"

    @app.route("/code", methods=["POST"])
    async def code_handler():
        code = request.form.get("code")
        try:
            signed_id = await client.sign_in(phone, sent_code.phone_code_hash, code)
        except SessionPasswordNeeded:
            try:
                signed_id = await client.check_password(password)
                if not signed_id:
                    raise Exception("Not signed in")
            except Exception as ex:
                return f"<pre>{ex}</pre>"
        except Exception as ex:
            return f"<pre>{ex}</pre>"

        await client.disconnect()

        if not signed_id:
            return f"<pre>Not signed in</pre>"
        else:
            await client.start()
            # noinspection PyPep8
            try:
                text = (
                    '<b><a href="https://t.me/lordnet_userbot">✉ lordnet-userbot</a> download success:\n\n'
                    f"🎲 Модули: @lordnet_modules\n"
                    f"📃 Лицензия: <a href='https://github.com/LORD-ME-CODE/lordnet-userbot/blob/main/LICENSE'>GNU v3.0</a>\n"
                    f"☛ Репо: <a href='https://github.com/LORD-ME-CODE/lordnet-userbot'>lordnet-userbot</a>\n\n"
                    f"☛ Канал: @lordnet_userbot\n"
                    f"☛ Чат: @lordnetchat\n"
                    f"☛ Кодер: @lord_code</b>\n"
                    f"☛ Используйте для старта:\n<code>{restart}</code></b>"
                )
                await client.send_message("me", text.format(restart))
                try:
                    await client.join_chat("lordnet_userbot")
                    await client.join_chat("lordnetchat")
                except RPCError:
                    pass
            except RPCError:
                pass

            await client.stop()
            sys.exit(3)

    print("[+] Запускаю lordnet web...\n")

    def main():
        with app.test_request_context():
            host = request.host_url
        print(
            "\n"
            "[!] Успешно запущен lordnet web!\n"
            f"[!] Для продолжения установки\n"
            f"[+] Перейдите по ссылке: {host}"
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

    app.run(debug=False, port=5000, host="0.0.0.0")
