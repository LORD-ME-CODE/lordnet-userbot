import os
import sys
from types import ModuleType


def restart():
    os.execvp(sys.executable, [sys.executable, "run.py"])


def get_module_name(insp: ModuleType):
    return insp.__name__
