import pytest
from typer.testing import CliRunner

from twbm import app

runner = CliRunner()


class TestSearch:
    def test_search_d(self, dal):
        result = runner.invoke(app, ["search", "-v"], input="d 1 2\n")
        print(result.stdout)
        assert result.exit_code == 0
        assert "Index 2 deleted" in result.stdout
        assert "Index 1 deleted" in result.stdout

    def test_search_p(self, dal):
        result = runner.invoke(app, ["search", "-v"], input="p 1 2\n")
        print(result.stdout)
        assert result.exit_code == 0
        assert "xxxxx" in result.stdout

    def test_search(self, dal):
        result = runner.invoke(app, ["search", "-v", "--np", "xxxxx"])
        print(result.stdout)
        assert result.exit_code == 0
        assert "xxxxx" in result.stdout

    def test_search_tags_exact(self, dal):
        result = runner.invoke(app, ["search", "-v", "--np", "-e", "aaa,bbb"])
        print(result.stdout)
        assert result.exit_code == 0
        assert "Found: 2" in result.stdout

    def test_search_tags_exact_none(self, dal):
        result = runner.invoke(app, ["search", "-v", "--np", "-e", "aaa"])
        print(result.stdout)
        assert result.exit_code == 0
        assert "Found: 0" in result.stdout

    def test_search_tags_exact_invalid(self, dal):
        result = runner.invoke(app, ["search", "-v", "--np", "-e", "aaa,", "bbb"])
        print(result.stdout)

    def test_search_non_existing_docs(self, dal):
        result = runner.invoke(app, ["docs", "-v"], input="1 2\n")
        print(result.stdout)
        assert result.exit_code == 0

    @pytest.mark.skip("Interactive Tests.")
    def test_search_browser_should_open(self, dal):
        result = runner.invoke(app, ["search", "-v"], input="1 2\n")
        print(result.stdout)
        assert result.exit_code == 1


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
        result = runner.invoke(
            app, ["add", "--title", "title1", "https://www.google.com"]
        )
        print(result.stdout)
        assert result.exit_code == 0

    def test_add_with_new_tags_yes(self, dal):
        result = runner.invoke(
            app,
            [
                "add",
                "--title",
                "title1",
                "https://www.google.com",
                "pa,pb",
                " pz",
                "PZ",
            ],
            input="y\n",
        )
        print(result.stdout)
        assert result.exit_code == 0

    def test_add_with_new_tags_no(self, dal):
        result = runner.invoke(
            app,
            [
                "add",
                "--title",
                "title1",
                "https://www.google.com",
                "pa,pb",
                " pz",
                "PZ",
            ],
            input="n\n",
        )
        print(result.stdout)
        assert "Create unknown_tags=['pa', 'pb', 'pz']" in result.stdout
        assert result.exit_code == 1


class TestTags:
    def test_tags(self, dal):
        result = runner.invoke(app, ["tags", "-v"])
        print(result.stdout)
        assert result.exit_code == 0

    def test_tags_related(self, dal):
        result = runner.invoke(app, ["tags", "-v", "xxx"])
        print(result.stdout)
        assert result.exit_code == 0
