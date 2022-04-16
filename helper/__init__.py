from .module import module, modules_dict, module_exists
from .cmd import restart, import_library, aimport_library, exception_str
from .misc import python_version, prefix, __version__

# noinspection PyUnresolvedReferences
from pyrogram.types import Message  # Shortcut for modules
