#!/usr/bin/env python

"""Tests for `eth_abi_tool` CLI"""

import json
from traceback import print_exception

import pytest
from click.testing import CliRunner

import eth_abi_tool
from eth_abi_tool import __version__, cli


def test_version():
    """Test reading version and module name"""
    assert eth_abi_tool.__name__ == "eth_abi_tool"
    assert __version__
    assert isinstance(__version__, str)


@pytest.fixture
def run():
    runner = CliRunner()

    # env = os.environ.copy()
    # env['EXTRA_ENV_VAR'] = 'VALUE'

    def _run(cmd, **kwargs):
        expect_exit_code = kwargs.pop("expect_exit_code", 0)
        expect_exception = kwargs.pop("expect_exception", None)
        # kwargs["env"] = env
        result = runner.invoke(cli, cmd, **kwargs)
        if result.exception:
            if expect_exception is None or not isinstance(
                result.exception, expect_exception
            ):
                print_exception(result.exception)
                assert False, result.exception
        else:
            assert result.exit_code == expect_exit_code, result.output
        return result

    return _run


def test_cli_none(run):
    result = run([], expect_exception=RuntimeError)
    assert "Usage" in result.output


def test_cli_help(run):
    result = run(["--help"])
    assert "Show this message and exit." in result.output


def test_cli_config_format_show(run):
    result = run(["config", "format", "show"])
    assert len(result.output)


def test_cli_config_format_set_none(run):
    result = run(["config", "format", "set"])
    assert result.exit_code == 0


def test_cli_config_format_set_fmt(run):
    result = run(["--fmt", "text", "config", "format", "set"])
    assert result.exit_code == 0


def test_cli_config_format_set_tablefmt(run):
    result = run(["--tablefmt", "plain", "config", "format", "set"])
    assert result.exit_code == 0


def test_cli_config_format_set_both(run):
    result = run(
        [
            "--fmt",
            "text",
            "--tablefmt",
            "fancy_grid",
            "config",
            "format",
            "set",
        ]
    )
    assert result.exit_code == 0


def test_cli_config_format_reset(run):
    result = run(["config", "format", "reset"])
    assert result.exit_code == 0


def test_cli_get_abi(run, address):
    result = run(["get", address])
    abi = json.loads(result.output)
    assert isinstance(abi, list)
    for a in abi:
        assert isinstance(a, dict)
