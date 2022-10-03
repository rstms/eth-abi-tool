"""ABI object"""

import json

import requests
from ratelimiter import RateLimiter

# rate limit to 5 calls per second
RATELIMIT = 5


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
        "Etherscan": {
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
        self.abi = None

    @RateLimiter(max_calls=RATELIMIT, period=1)
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
            self.abi = json.loads(result["result"])
        return self.abi

    def _select_elements(self, _type):
        ret = {}
        for i in self.abi:
            if i.get("type", None) == _type:
                name = i.get("name", None)
                if name:
                    ret[name] = i
        return ret

    def functions(self):
        return self._select_elements("function")

    def function_names(self):
        return list(self.functions().keys())

    def function(self, name):
        return self.functions()[name]

    def events(self):
        return self._select_elements("event")

    def event_names(self):
        return list(self.events().keys())

    def event(self, event):
        return self.events()[event]

    def topic(self, *, name=None, event=None):
        """generate event signature hash"""
        from eth_utils import event_abi_to_log_topic, to_hex

        if name is not None:
            event = self.event(name)

        topic = event_abi_to_log_topic(event)
        ret = to_hex(topic)
        return ret
