import os

import pytest
from click.testing import CliRunner

from pubscraper import main
from pubscraper.version import __version__

RESPONSE_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "responses_main"
)


def get_response_text(response_file):
    with open(response_file) as f:
        response_content = f.read()
    return response_content


@pytest.fixture()
def runner():
    return CliRunner()


def test_print_help_succeeds(runner):
    response_text = get_response_text(os.path.join(RESPONSE_DIR, "help.txt"))
    result = runner.invoke(main.main, ["--help"])
    assert result.exit_code == 0
    assert result.output == response_text


def test_print_version(runner):
    version_string = "version {}".format(__version__)
    result = runner.invoke(main.main, ["--version"])
    assert result.exit_code == 0
    assert version_string in result.output


def test_bad_input_file(runner):
    result = runner.invoke(main.main, ["-i nonexistent_input.txt"])
    assert result.exit_code == 1


def test_bad_api_selection(runner):
    result = runner.invoke(main.main, ["-a BadAPI"])
    assert result.exit_code == 2


def test_log_level(runner):
    result = runner.invoke(main.main, ["--log-level DEBUG"])
    assert "DEBUG" in result.output


def test_print_list_succeeds(runner):
    response_text = get_response_text(os.path.join(RESPONSE_DIR, "list.txt"))
    result = runner.invoke(main.main, ["--list"])
    assert result.exit_code == 0
    assert result.output == response_text
