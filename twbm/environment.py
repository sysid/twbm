"""Default environment
Edit service environment to override
"""
################################################################################
# Base Environment
################################################################################
import os
import sys
from pathlib import Path
from typing import Any, Optional, Union

from pydantic import BaseSettings

env_file_sentinel = str(object())

RUN_ENV = os.environ.get("RUN_ENV", "local").lower()
ROOT_DIR = Path(__file__).parent.parent.absolute()
env_path = ROOT_DIR / f".env.{RUN_ENV}"

if not os.path.isfile(env_path):
    print("-E- No env file found for environment. Exiting.")
    sys.exit()


class Environment(BaseSettings):
    run_env: str
    log_level: str = "INFO"
    bm_db_url: str = "sqlite://db/bm.db"

    def __init__(
            self,
            _env_file: Union[Path, str, None] = env_file_sentinel,
            _env_file_encoding: Optional[str] = None,
            **values: Any,
    ):
        super().__init__(
            _env_file=_env_file, _env_file_encoding=_env_file_encoding, **values
        )
        self.run_env = self.run_env.lower()


config = Environment(_env_file=env_path)
_ = None
