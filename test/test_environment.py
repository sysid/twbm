from twbm.environment import config


def test_env():
    assert config.dbfile == "test/tests_data/bm_test.db"
