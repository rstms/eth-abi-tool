# abi module test

import os

from eth_abi_tool import ABI


def test_abi_get(explorer, chain, address):

    key = os.environ["EXPLORER_API_KEY"]

    abi = ABI(explorer, chain, key)

    contract_abi = abi.get(address)

    assert isinstance(contract_abi, list)
    for a in contract_abi:
        assert isinstance(a, dict)
