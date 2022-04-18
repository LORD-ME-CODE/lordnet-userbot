from .module import module, modules_dict, module_exists, load_module, escape_html
from .cmd import restart, import_library, aimport_library, exception_str
from .misc import python_version, prefix, __version__, session
from .db import db

# noinspection PyUnresolvedReferences
from pyrogram import Client  # Shortcut for modules

# noinspection PyUnresolvedReferences
from pyrogram.types import Message  # Shortcut for modules
