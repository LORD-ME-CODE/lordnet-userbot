import os
import sys


def restart():
    os.execvp(sys.executable, [sys.executable, "main.py"])
