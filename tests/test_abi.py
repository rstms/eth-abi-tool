# abi module test

import os

import pytest

from eth_abi_tool import ABI


@pytest.fixture
def abi(explorer, chain, address):
    key = os.environ["EXPLORER_API_KEY"]
    abi = ABI(explorer, chain, key)
    abi.get(address)
    return abi


def test_abi_get(abi, address):
    contract_abi = abi.get(address)
    assert isinstance(contract_abi, list)
    for a in contract_abi:
        assert isinstance(a, dict)


def test_abi_functions(abi, expected_functions):
    functions = abi.functions()
    assert isinstance(functions, dict)
    assert set(functions.keys()) == set(expected_functions)
    for name, function_abi in functions.items():
        assert isinstance(name, str)
        assert isinstance(function_abi, dict)
        assert function_abi["type"] == "function"


def test_abi_function_names(abi, expected_functions):
    names = abi.function_names()
    assert set(names) == set(expected_functions)


def test_abi_events(abi, expected_events):
    events = abi.events()
    assert isinstance(events, dict)
    assert set(events.keys()) == set(expected_events)
    for name, event in events.items():
        assert isinstance(name, str)
        assert isinstance(event, dict)
        assert event["type"] == "event"


def test_abi_event_names(abi, expected_events):
    names = abi.event_names()
    assert set(names) == set(expected_events)


def test_abi_topic_by_name(abi, test_event_name, expected_topic):
    topic = abi.topic(name=test_event_name)
    assert topic == expected_topic


def test_abi_topic_by_event_abi(abi, test_event_name, expected_topic):
    event_abi = abi.event(test_event_name)
    topic = ABI().topic(event=event_abi)
    assert topic == expected_topic
