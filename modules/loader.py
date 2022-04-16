from helper import module, Message, modules_dict, prefix, module_exists


@module(
    cmds=["load", "unload", "lm", "ulm", "loadmod", "unloadmod"],
    desc="Load/unload modules",
    args=["name"],
)
async def loader_cmd(_, message: Message):
    cmd = message.command[0]
    if cmd in ["load", "lm", "loadmod"]:
        if len(message.command) == 1:
            await message.reply("<b>🙄 Please specify a module to load</b>")
            return
        name = message.command[1].lower()
        if modules_dict.module_in(name):
            await message.reply(
                f"<b>🙄 Module <code>{name}</code> already loaded\n"
                f"🔃 Type <code>{prefix()}updatemod</code> to update it</b>"
            )
            return
        if not await module_exists(name):
            await message.reply(f"<b>🙄 Module <code>{name}</code> does not exist\n")
            return
    else:
        if len(message.command) == 1:
            await message.reply("<b>🙄 Please specify a module to unload</b>")
            return
        name = message.command[1].lower()
        if not modules_dict.module_in(name):
            await message.reply(f"<b>🙂 Module <code>{name}</code> not loaded</b>")
            return
