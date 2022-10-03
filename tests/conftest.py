# test fixtures

import pytest


@pytest.fixture
def explorer():
    return "etherscan"


@pytest.fixture
def chain():
    return "goerli"


@pytest.fixture
def address():
    return "0x6e0e0802A69522533988ae0AD3A7E9ebD3B2c05D"
