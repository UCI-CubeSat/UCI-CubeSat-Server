from sys import platform as _platform
from os.path import expanduser


def getRoot():
    if _platform == "linux" or _platform == "linux2":
        pass
    elif _platform == "darwin":
        pass
    elif _platform == "win32":
        pass
    elif _platform == "win64":
        pass

    return expanduser("~")
