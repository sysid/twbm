import pytest
from typer.testing import CliRunner

from twbm import app

runner = CliRunner()


def test_search_p():
    result = runner.invoke(app, ["search", "-v"], input="p 1 2\n")
    print(result.stdout)
    assert result.exit_code == 0
    assert "xxxxx" in result.stdout


def test_search():
    result = runner.invoke(app, ["search", "-v", "--np", "xxxxx"])
    print(result.stdout)
    assert result.exit_code == 0
    assert "xxxxx" in result.stdout


@pytest.mark.skip("Notnworking: not allowed operations: fileno()")
def test_upgrade(dal):
    result = runner.invoke(app, ["update", "-v", "-n", "aaa", "2,3"])
    print(result.stdout)
    assert result.exit_code == 0


def test_delete(dal):
    result = runner.invoke(app, ["delete", "-v", "6"])
    print(result.stdout)


class TestAddUrl:
    def test_add(self, dal):
        result = runner.invoke(app, ["add", "--title", "title1", "https://www.google.com"])
        print(result.stdout)
        assert result.exit_code == 0

    def test_add_with_new_tags_yes(self, dal):
        result = runner.invoke(app, ["add", "--title", "title1", "https://www.google.com", "pa,pb", " pz", "PZ"],
                               input="y\n")
        print(result.stdout)
        assert result.exit_code == 0

    def test_add_with_new_tags_no(self, dal):
        result = runner.invoke(app, ["add", "--title", "title1", "https://www.google.com", "pa,pb", " pz", "PZ"],
                               input="n\n")
        print(result.stdout)
        assert "Create unknown_tags=['pa', 'pb', 'pz']" in result.stdout
        assert result.exit_code == 1
