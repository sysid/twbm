import logging
import os
import subprocess
import sys
import webbrowser
from pathlib import Path

ROOT_DIR = Path(__file__).parent.absolute()
_log = logging.getLogger(__name__)

if sys.platform.startswith("win32"):
    pass
elif sys.platform.startswith("linux"):
    OS_OPEN = "xdg-open"
# Linux-specific code here...
elif sys.platform.startswith("darwin"):
    OS_OPEN = "open"
else:
    OS_OPEN = None


def open_it(uri):
    if OS_OPEN is None:
        _log.error(f"Unknown OS architecture: {sys.platform}")
        return

    _log.debug(f"{uri=}")
    p = Path.home()  # default setting

    if uri.startswith("http"):
        _log.debug(f"Http Link")
        # p = uri
        webbrowser.open(uri, new=2)
        return
    elif uri[0] in "/,.,~,$":
        if uri.startswith("/"):
            _log.debug(f"Absolute path.")
            p = Path(uri)
        elif uri.startswith("~"):
            _log.debug(f"Path with prefix tilde.")
            p = Path(uri).expanduser().absolute()
        elif uri.startswith("$"):
            _log.debug(f"Path with environment prefix.")
            p = Path(uri)
            env_path = os.getenv(p.parts[0].strip("$"), None)
            if env_path is None:
                _log.warning(f"{p.parts[0]} not set in environment. Cannot proceed.")
                return
            p = Path(env_path) / Path(*p.parts[1:])
        elif uri.startswith("."):
            _log.debug(f"Relative path: {uri}, working dir: {os.getcwd()}")
            p = Path(uri).absolute()

        if not p.exists():
            _log.warning(f"{p} does not exists.")
            return
    else:
        _log.warning(f"Unknown protocol: {uri=}")
        return

    _log.info(f"Opening: {p}")
    subprocess.run([OS_OPEN, p])
