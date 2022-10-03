"""Console script for eth_abi_tool."""


import json
import sys
from pathlib import Path

import click
import tablib
import tabulate
from box import Box

from .abi import ABI
from .exception_handler import ExceptionHandler
from .version import __timestamp__, __version__

header = f"{__name__.split('.')[0]} v{__version__} {__timestamp__}"

OUTPUT_FORMATS = ["json", "yaml", "csv", "cli", "text"]
DEFAULT_FMT = "json"
TABLE_FORMATS = tabulate._table_formats
DEFAULT_TABLEFMT = "pretty"

EXPLORERS = list(ABI.EXPLORERS.keys())
CHAINS = list(ABI.EXPLORERS[EXPLORERS[0]].keys())


def config_read(ctx):
    if ctx.obj.config_file.is_file():
        ctx.obj.config = Box(json.loads(ctx.obj.config_file.read_text()))
    else:
        ctx.obj.config = Box({})
    ctx.obj.config.setdefault("contracts", {})
    ctx.obj.config.setdefault("format", {})
    return ctx.obj.config


def config_write(ctx):
    ctx.obj.config_file.write_text(json.dumps(dict(ctx.obj.config), indent=2))


def get_default_format(ctx, key):
    return ctx.obj.config.format.get(key, DEFAULT_FMT)


def get_format(ctx, key):
    return ctx.obj.get(key) or get_default_format(ctx, key)


def output_table(ctx, data):
    fmt = get_format(ctx, "fmt")
    if fmt in ["cli", "text"]:
        tablefmt = get_format(ctx, "tablefmt")
        output = data.export("cli", tablefmt=tablefmt)
    elif fmt == "json":
        output = data.export(fmt)
        if not ctx.obj.compact:
            output = json.dumps(json.loads(output), indent=2)
    else:
        raise ValueError(f"unexpected {fmt=}")
    click.echo(output)


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
    "-C",
    "--chain",
    type=click.Choice(CHAINS),
    envvar="EXPLORER_CHAIN",
    show_envvar=True,
    help="Chain Name",
)
@click.option(
    "-e",
    "--explorer",
    type=click.Choice(EXPLORERS),
    envvar="EXPLORER_GATEWAY",
    show_envvar=True,
    help="Blockchain Explorer Name",
)
@click.option(
    "-c",
    "--config-file",
    type=click.Path(dir_okay=False, writable=True, path_type=Path),
    default=Path.home() / ".eth-abi-tool",
    help="config file",
)
@click.option(
    "-f",
    "--fmt",
    type=click.Choice(OUTPUT_FORMATS),
    default=None,
    help="output format",
)
@click.option(
    "-T",
    "--tablefmt",
    type=click.Choice(TABLE_FORMATS),
    default=None,
    help="text table output format",
)
@click.option(
    "-J/-j",
    "--compact/--no-compact",
    is_flag=True,
    default=None,
    help="compact json format",
)
@click.pass_context
def cli(ctx, **kwargs):
    """Ethereum Contract ABI Utility"""
    ctx.obj = Box(kwargs)
    ctx.obj.ehandler = ExceptionHandler(ctx.obj.debug)
    ctx.obj.abi = ABI(ctx.obj.explorer, ctx.obj.chain, ctx.obj.key)
    if ctx.obj.compact is not None:
        ctx.obj.fmt = "json"
    if ctx.obj.fmt == "text":
        ctx.obj.fmt = "cli"
    config_read(ctx)


@cli.group
@click.pass_context
def config(ctx):
    """config commands"""
    pass


@config.group
@click.pass_context
def format(ctx):
    """output format config"""
    pass


@format.command(name="reset")
@click.pass_context
def config_format_reset(ctx):
    """reset default output format"""
    ctx.obj.config.format.fmt = DEFAULT_FMT
    ctx.obj.config.format.tablefmt = DEFAULT_TABLEFMT
    config_write(ctx)


@format.command(name="set")
@click.pass_context
def config_format_set(ctx):
    """set current output format selections as default"""
    ctx.obj.config.format.fmt = ctx.obj.fmt or DEFAULT_FMT
    ctx.obj.config.format.tablefmt = ctx.obj.tablefmt or DEFAULT_TABLEFMT
    config_write(ctx)


@format.command(name="show")
@click.pass_context
def config_format_show(ctx):
    """display output format default settings"""
    data = tablib.Dataset()
    data.append(("fmt", get_default_format(ctx, "fmt")))
    data.append(("tablefmt", get_default_format(ctx, "tablefmt")))
    data.headers = ["setting", "value"]
    ctx.obj.fmt = "cli"
    ctx.obj.tablefmt = "pretty"
    output_table(ctx, data)


@config.group
@click.pass_context
def contract(ctx):
    """contract config"""
    pass


@contract.command(name="add")
@click.argument("name", type=str)
@click.argument("address", type=str)
@click.pass_context
def config_contract_add(ctx, name, address):
    """add contract name and address"""
    from eth_utils import is_address

    if not is_address(address):
        raise ValueError(f"{address=}")
    ctx.obj.config.contracts[name] = address
    config_write(ctx)


@contract.command(name="delete")
@click.argument("name", type=str)
@click.pass_context
def config_contract_delete(ctx, name):
    """delete named contract"""
    del ctx.obj.config.contracts[name]
    config_write(ctx)


@contract.command(name="list")
@click.pass_context
def config_contract_list(ctx):
    """list configured contract addresses"""
    from eth_utils import to_normalized_address

    contracts = ctx.obj.config.contracts
    data = tablib.Dataset()
    for name, address in contracts.items():
        data.append([name, to_normalized_address(address)])
    data.headers = ["Name", "Address"]
    output_table(ctx, data)


@cli.command
@click.option("-f", "--functions", is_flag=True, help="select only functions")
@click.option("-e", "--events", is_flag=True, help="select only events")
@click.option(
    "-h/-H",
    "--header/--no-header",
    is_flag=True,
    default=True,
    help="select header output",
)
@click.option("-n", "--name", is_flag=True, help="switch name output")
@click.option("-a", "--abi", is_flag=True, help="select abi output")
@click.option("-t", "--topic", is_flag=True, help="select topic0 hex output")
@click.option("-c", "--complete", is_flag=True, help="output complete ABI")
@click.argument("contract", type=str)
@click.argument("abi-name", type=str, required=False)
@click.pass_context
def get(
    ctx,
    functions,
    events,
    header,
    name,
    abi,
    topic,
    complete,
    contract,
    abi_name,
):
    """query block explorer and output contract ABI as json"""
    from eth_utils import is_address

    if not any([functions, events, header, name, abi, topic]):
        complete = True

    if functions and not any([events, header, name, abi, topic]):
        name = True

    if events and not any([functions, header, name, abi, topic]):
        name = True

    if contract in ctx.obj.config.contracts.keys():
        contract = ctx.obj.config.contracts[contract]
    elif not is_address(contract):
        raise ValueError(f"{contract=}")

    result = ctx.obj.abi.get(contract)

    if complete:
        if ctx.obj.compact:
            indent = None
        else:
            indent = 2
        click.echo(json.dumps(result, indent=indent))
    else:
        if functions:
            abi_type = "function"
        elif events:
            abi_type = "event"
        else:
            abi_type = None
        output_abi(ctx, result, abi_type, header, name, abi, topic, abi_name)


def output_abi(
    ctx,
    contract_abi,
    abi_type,
    enable_header,
    enable_name,
    enable_abi,
    enable_topic,
    name=None,
):
    """format abi output

    ctx.obj.header: ------- bool include header
    contract_abi: --------- list of abi elements
    abi_type: ------------- None / 'function' / 'event'
    enable_header: bool --- include header in output
    enable_name: bool ----- include name in output
    enable_abi: bool ------ include abi in output
    enable_topic: bool ---- include hex topic0 in output
    name: str ------------- include only matching rows if not None

    """

    data = tablib.Dataset()
    for abi in [Box(a) for a in contract_abi]:
        # skip rows with no name
        if "name" not in abi:
            continue
        # if name specified, skip non-matching rows
        if name is not None and abi.name != name:
            continue

        # if abi_type specified, skip non-matching rows
        if abi_type is not None and abi.type != abi_type:
            continue

        row = []
        header = []

        if enable_name:
            header.append("name")
            row.append(abi.name)
        if enable_abi:
            header.append("abi")
            row.append(abi.to_dict())
            # if ctx.obj.get('fmt') == 'json':
            #    row.append(abi.to_dict())
            # else
            #    row.append(compressed_json(abi))
        if enable_topic:
            header.append("topic")
            if abi.type == "event":
                topic = ABI().topic(event=abi)
            else:
                topic = ""
            row.append(topic)

        if row is not None and len(row) > 0:
            data.append(tuple(row))

        if len(header) > 0 and enable_header:
            data.headers = header
    output_table(ctx, data)


def compressed_json(abi):
    return json.dumps(abi.to_dict(), separators=[":", ","])


if __name__ == "__main__":
    sys.exit(cli())  # pragma: no cover
