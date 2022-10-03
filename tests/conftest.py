# test fixtures

import pytest


@pytest.fixture
def explorer():
    return "Etherscan"


@pytest.fixture
def chain():
    return "goerli"


@pytest.fixture
def address():
    return "0x6e0e0802A69522533988ae0AD3A7E9ebD3B2c05D"


@pytest.fixture
def test_event_name():
    return "RoleGranted"


@pytest.fixture
def expected_topic():
    return "0x2f8788117e7eff1d82e926ec794901d17c78024a50270940304540a733656f0d"


@pytest.fixture
def expected_functions():
    return [
        "DEFAULT_ADMIN_ROLE",
        "MINTER_ROLE",
        "PAUSER_ROLE",
        "approve",
        "authorizeEthersieve",
        "balanceOf",
        "burn",
        "contractURI",
        "getApproved",
        "getRoleAdmin",
        "grantRole",
        "hasRole",
        "isApprovedForAll",
        "name",
        "ownerOf",
        "pause",
        "paused",
        "renounceRole",
        "revokeRole",
        "safeMint",
        "safeTransferFrom",
        "setApprovalForAll",
        "setTokenURI",
        "supportsInterface",
        "symbol",
        "tokenURI",
        "transferFrom",
        "unpause",
    ]


@pytest.fixture
def expected_events():
    return [
        "Approval",
        "ApprovalForAll",
        "Paused",
        "RoleAdminChanged",
        "RoleGranted",
        "RoleRevoked",
        "Transfer",
        "Unpaused",
    ]
