import logging

import pytest

from twbm.handle_uri import open_it


@pytest.mark.skip("Only working when run in isolaotion, caplog problem?")
class TestOpenIt:
    @pytest.mark.parametrize(
        ("uri", "result"),
        (
            ("https://www.google.com", "https://www.google.com"),
            (
                "$HOME/dev/py/twbm/test/tests_data/test.pptx",
                "/Users/Q187392/dev/py/twbm/test/tests_data/test.pptx",
            ),
            ("/Users/Q187392/dev", "/Users/Q187392/dev"),
            ("~/dev", "/Users/Q187392/dev"),
        ),
    )
    def test_open_it(self, mocker, uri, result, caplog):
        # caplog.set_level(logging.DEBUG)
        with caplog.at_level(logging.DEBUG):
            webbrowser_open = mocker.patch("twbm.handle_uri.webbrowser.open")
            subprocess_run = mocker.patch("twbm.handle_uri.subprocess.run")
            open_it(uri)

            if uri.startswith("http"):
                webbrowser_open.assert_called()
            else:
                subprocess_run.assert_called()

        assert result in caplog.text
