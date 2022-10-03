"""Top-level package for eth-abi-tool."""

from .abi import ABI
from .cli import cli
from .version import __author__, __email__, __timestamp__, __version__

__all__ = ["cli", "ABI", __version__, __timestamp__, __author__, __email__]
