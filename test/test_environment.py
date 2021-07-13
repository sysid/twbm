import os

os.environ[
    "RUN_ENV"
] = "testing"  # Gotcha: make sure environment setup is before app is sourced
from twbm.environment import config


def test_env():
    assert config.dbfile == "./test/tests_data/bm_test.db"
