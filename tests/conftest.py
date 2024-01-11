"""Shared fixtures for all pantos.client.lbrary.business package tests.

"""
import pytest

from pantos.client.library.blockchains.base import BlockchainClient
from pantos.client.library.constants import TOKEN_SYMBOL_PAN
from pantos.common.blockchains.base import Blockchain
from pantos.common.entities import BlockchainAddress
from pantos.common.entities import ServiceNodeBid
from pantos.common.types import PrivateKey

_SERVICE_NODE_1 = BlockchainAddress(
    '0x5188287E724140aa3C432dCfE69E00992aF09d09')

_SERVICE_NODE_2 = BlockchainAddress(
    '0xbD5b933785096837103de4a7a25b75b23153EAbE')

_TOKEN_ADDRESS = BlockchainAddress(
    '0x53bAFF6C5A3F2F578C78eC8e66464C31aF62A7D6')

_PRIVATE_KEY = PrivateKey(
    '0x0000000000000000000000000000000000000000000000000000000000000000')

_BIDS_1 = [
    ServiceNodeBid(Blockchain.CELO, Blockchain.CRONOS, 100, 10, 100, 'sig1'),
    ServiceNodeBid(Blockchain.CELO, Blockchain.CRONOS, 10, 10, 100, 'sig2'),
    ServiceNodeBid(Blockchain.CELO, Blockchain.CRONOS, 1000, 10, 100, 'sig3'),
    ServiceNodeBid(Blockchain.CELO, Blockchain.CRONOS, 1, 10, 100, 'sig4')
]

_BIDS_2 = [
    ServiceNodeBid(Blockchain.CELO, Blockchain.CRONOS, 200, 10, 100, 'sig2'),
    ServiceNodeBid(Blockchain.CELO, Blockchain.CRONOS, 20, 10, 100, 'sig4'),
    ServiceNodeBid(Blockchain.CELO, Blockchain.CRONOS, 2000, 10, 100, 'sig5'),
    ServiceNodeBid(Blockchain.CELO, Blockchain.CRONOS, 2, 10, 100, 'sig6')
]


@pytest.fixture(scope='module')
def service_node_1():
    return _SERVICE_NODE_1


@pytest.fixture(scope='module')
def service_node_2():
    return _SERVICE_NODE_2


@pytest.fixture(scope='module')
def bids_1():
    return _BIDS_1


@pytest.fixture(scope='module')
def bids_2():
    return _BIDS_2


@pytest.fixture(scope='module')
def token_address():
    return _TOKEN_ADDRESS


@pytest.fixture(scope='module')
def config(scope='module'):
    return {
        'hub': '0x308eF9f94a642A31D9F9eA83f183544027A9742D',
        'forwarder': '0x308eF9f94a642A31D9F9eA83f183544027A9742D',
        'tokens': {
            TOKEN_SYMBOL_PAN: '0x53bAFF6C5A3F2F578C78eC8e66464C31aF62A7D6'
        }
    }


@pytest.fixture(scope='module')
def transfer_signature_request():
    return BlockchainClient.ComputeTransferSignatureRequest(
        sender_private_key=_PRIVATE_KEY, recipient_address=_SERVICE_NODE_2,
        token_address=_TOKEN_ADDRESS, token_amount=100,
        service_node_address=_SERVICE_NODE_1, service_node_bid=_BIDS_1[0],
        valid_until=1000)


@pytest.fixture(scope='module')
def transfer_from_signature_request():
    return BlockchainClient.ComputeTransferFromSignatureRequest(
        destination_blockchain=Blockchain.CELO,
        sender_private_key=_PRIVATE_KEY, recipient_address=_SERVICE_NODE_2,
        source_token_address=_TOKEN_ADDRESS,
        destination_token_address=_TOKEN_ADDRESS, token_amount=100,
        service_node_address=_SERVICE_NODE_1, service_node_bid=_BIDS_1[0],
        valid_until=1000)
