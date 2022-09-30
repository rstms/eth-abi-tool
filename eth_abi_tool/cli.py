"""Console script for eth_abi_tool."""

import json
import sys
from pathlib import Path

import click
import requests
import tablib
from box import Box

from .exception_handler import ExceptionHandler
from .version import __timestamp__, __version__

header = f"{__name__.split('.')[0]} v{__version__} {__timestamp__}"

EXPLORER_NAMES = ["Etherscan"]
CHAINS = {
    "mainnet": {"Etherscan": "https://api.etherscan.io"},
    "kovan": {"Etherscan": "https://api-kovan.etherscan.io"},
    "goerli": {"Etherscan": "https://api-goerli.etherscan.io"},
    "rinkeby": {"Etherscan": "https://api-rinkeby.etherscan.io"},
    "ropsten": {"Etherscan": "https://api-ropsten.etherscan.io"},
    "sepolia": {"Etherscan": "https://api-sepolia.etherscan.io"},
}


def config_read(ctx):
    if ctx.obj.config_file.is_file():
        ctx.obj.config = Box(json.loads(ctx.obj.config_file.read_text()))
    else:
        ctx.obj.config = Box({})
    return ctx.obj.config


def config_write(ctx):
    ctx.obj.config_file.write_text(json.dumps(dict(ctx.obj.config), indent=2))


@click.group("abi")
@click.version_option(message=header)
@click.option("-d", "--debug", is_flag=True, help="debug mode")
@click.option(
    "-k",
    "--key",
    type=str,
    envvar="EXPLORER_API_KEY",
    show_envvar=True,
    help="Explorer API Key",
)
@click.option(
    "-c",
    "--chain",
    type=click.Choice(list(CHAINS.keys())),
    envvar="EXPLORER_CHAIN",
    show_envvar=True,
    help="Chain Name",
)
@click.option(
    "-e",
    "--explorer",
    type=click.Choice(EXPLORER_NAMES),
    envvar="EXPLORER_GATEWAY",
    show_envvar=True,
    help="Blockchain Explorer Name",
)
@click.option(
    "-f",
    "--config-file",
    type=click.Path(dir_okay=False, writable=True, path_type=Path),
    default=Path.home() / ".eth-abi-tool",
    help="config file",
)
@click.pass_context
def cli(ctx, **kwargs):
    """Ethereum Contract ABI Utility"""
    ctx.obj = Box(kwargs)
    ctx.obj.ehandler = ExceptionHandler(ctx.obj.debug)
    ctx.obj.url = CHAINS[ctx.obj.chain][ctx.obj.explorer]
    config_read(ctx)


@cli.group
@click.pass_context
def config(ctx):
    """config commands"""


@config.group
@click.pass_context
def contract(ctx):
    """config contract commands"""


@contract.command
@click.argument("name", type=str)
@click.argument("address", type=str)
@click.pass_context
def add(ctx, name, address):
    """add contract name and address"""
    from eth_utils import is_address
    if not is_address(address):
        raise ValueError(f"{address=}")
    ctx.config.setdefault("contracts", {})
    ctx.config.contracts[name] = address
    config_write(ctx)


@contract.command
@click.argument("name", type=str)
@click.pass_context
def delete(ctx, name):
    """delete named contract"""
    ctx.config.setdefault("contracts", {})
    del ctx.config.contracts[name]
    config_write(ctx)


@contract.command
@click.pass_context
def list(ctx):
    """list configured contract addresses"""
    from eth_utils import to_normalized_address
    contracts = ctx.obj.config.contracts
    data = tablib.Dataset()
    for name, address in contracts.items():
        data.append([name, to_normalized_address(address)])
    data.headers = ["Name", "Address"]
    click.echo(data.export("cli"))


@cli.command
@click.pass_context
def get(ctx, contract_address):
    """query block explorer and output contract ABI as json"""
    params = dict(
        module="contract",
        action="getabi",
        address=contract_address,
        apikey=ctx.obj.key,
    )
    url = f"{ctx.obj.url}/api"
    response = requests.get(url, params=params)
    if not response.ok:
        response.raise_for_status()
    result = response.json()
    click.echo(json.dumps(result, indent=2))


if __name__ == "__main__":
    sys.exit(cli())  # pragma: no cover
