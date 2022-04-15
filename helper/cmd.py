import os
import sys


def restart():
    os.execvp(sys.executable, [sys.executable, "run.py"])
