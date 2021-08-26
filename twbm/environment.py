"""Default environment
Edit service environment to override
"""
################################################################################
# Base Environment
################################################################################
from pathlib import Path

from pydantic import BaseSettings

ROOT_DIR = Path(__file__).parent.absolute()


class Environment(BaseSettings):
    log_level: str = "INFO"
    twbm_db_url: str = "sqlite:///db/bm.db"

    @property
    def dbfile(self):
        return f"{self.twbm_db_url.split('sqlite:///')[-1]}"


config = Environment()
_ = None
