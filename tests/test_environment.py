from twbm.environment import config


def test_env():
    assert config.dbfile == "tests/tests_data/bm_test.db"
