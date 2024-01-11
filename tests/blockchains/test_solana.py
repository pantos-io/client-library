import unittest.mock

import pytest

from pantos.client.library.blockchains.solana import SolanaClient
from pantos.client.library.blockchains.solana import SolanaClientError
from pantos.common.blockchains.base import Blockchain


@pytest.fixture(scope='module')
@unittest.mock.patch.object(SolanaClient, '__init__', lambda self: None)
def solana_client():
    return SolanaClient()


def test_get_blockchain_correct(solana_client):
    assert solana_client.get_blockchain() is Blockchain.SOLANA
    assert SolanaClient.get_blockchain() is Blockchain.SOLANA


def test_get_error_class_correct(solana_client):
    assert solana_client.get_error_class() is SolanaClientError
    assert SolanaClient.get_error_class() is SolanaClientError


def test_is_valid_recipient_address_not_implemented(solana_client):
    recipient_address = "0x0000000000000000000000000000000000000000"
    with pytest.raises(NotImplementedError):
        solana_client.is_valid_recipient_address(recipient_address)


def test_compute_transfer_from_signature_not_implemented(solana_client):
    with pytest.raises(NotImplementedError):
        solana_client.compute_transfer_from_signature(None)


def test_compute_transfer_signature_not_implemented(solana_client):
    with pytest.raises(NotImplementedError):
        solana_client.compute_transfer_signature(None)


def test_read_service_node_addresses_not_implemented(solana_client):
    with pytest.raises(NotImplementedError):
        solana_client.read_service_node_addresses()


def test_read_service_node_bid_not_implemented(solana_client):
    with pytest.raises(NotImplementedError):
        solana_client.read_service_node_bid(None, 0)


def test_read_service_node_bids_not_implemented(solana_client):
    with pytest.raises(NotImplementedError):
        solana_client.read_service_node_bids(None, 0)


def test_read_service_node_url_not_implemented(solana_client):
    with pytest.raises(NotImplementedError):
        solana_client.read_service_node_url(None)


def test_read_token_decimals_not_implemented(solana_client):
    with pytest.raises(NotImplementedError):
        solana_client.read_token_decimals(None)
