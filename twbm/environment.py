"""Default environment
Edit service environment to override
"""
################################################################################
# Base Environment
################################################################################
import sys
from pathlib import Path

from pydantic import BaseSettings

ROOT_DIR = Path(__file__).parent.absolute()

if sys.platform.startswith("win32"):
    OS_OPEN = "explorer.exe"
elif sys.platform.startswith("linux"):
    OS_OPEN = "xdg-open"
# Linux-specific code here...
elif sys.platform.startswith("darwin"):
    OS_OPEN = "open"
else:
    OS_OPEN = None


class Environment(BaseSettings):
    log_level: str = "INFO"
    twbm_db_url: str = "sqlite:///db/bm.db"

    @property
    def dbfile(self):
        return f"{self.twbm_db_url.split('sqlite:///')[-1]}"


config = Environment()
_ = None
