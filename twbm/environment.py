"""Default environment
Edit service environment to override
"""
################################################################################
# Base Environment
################################################################################

from pydantic import BaseSettings


class Environment(BaseSettings):
    log_level: str = "INFO"
    twbm_db_url: str = "sqlite:///db/bm.db"


config = Environment()
_ = None
