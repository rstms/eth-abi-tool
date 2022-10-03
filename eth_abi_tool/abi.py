"""ABI object"""

import json

import requests


class ABIException(Exception):
    pass


class ABIQueryFailure(ABIException):
    """Explorer API query failed"""

    pass


class ABIError(ABIException):
    """Explorer API returned error"""

    pass


class ABI:

    EXPLORERS = {
        "etherscan": {
            "mainnet": {"url": "https://api.etherscan.io/api"},
            "kovan": {"url": "https://api-kovan.etherscan.io/api"},
            "goerli": {"url": "https://api-goerli.etherscan.io/api"},
            "rinkeby": {"url": "https://api-rinkeby.etherscan.io/api"},
            "ropsten": {"url": "https://api-ropsten.etherscan.io/api"},
            "sepolia": {"url": "https://api-sepolia.etherscan.io/api"},
        }
    }

    def __init__(self, explorer=None, chain=None, key=None):
        self.explorer = explorer or list(self.EXPLORERS.keys())[0]
        self.chain = chain or list(self.EXPLORERS[self.explorer].keys())[0]
        self.url = self.EXPLORERS[self.explorer][self.chain]["url"]
        self.key = key

    def get(self, contract_address, key=None):
        from eth_utils import to_normalized_address

        key = key or self.key
        address = to_normalized_address(contract_address)
        params = dict(
            module="contract", action="getabi", address=address, apikey=key
        )
        response = requests.get(self.url, params=params)
        if not response:
            raise ABIQueryFailure(f"{response}")
        result = response.json()
        if result["status"] != "1" or result["message"] != "OK":
            raise ABIError(f"{result}")
        else:
            result = json.loads(result["result"])
        return result
