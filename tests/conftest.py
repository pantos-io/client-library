"""Shared fixtures for all pantos.client.library package tests.

"""
import hexbytes
import pytest
from pantos.common.blockchains.base import Blockchain
from pantos.common.entities import BlockchainAddress
from pantos.common.entities import ServiceNodeBid
from pantos.common.types import PrivateKey

from pantos.client.library.blockchains.base import BlockchainClient
from pantos.client.library.constants import TOKEN_SYMBOL_PAN

_BLOCK_NUMBER = 1

_TRANSACTION_HASH = hexbytes.HexBytes(
    '3273482cfbf640bd5a7056fc3fd418275d2537bb49638035e19f2c4ebcf2e3d9')

_SOURCE_TRANSFER_ID = 2

_DESTINATION_TRANSFER_ID = 3

_SENDER = BlockchainAddress('0x4958c0CdDb1649e8da454657733BA7AeC7069765')

_RECIPIENT = BlockchainAddress('0xDc825BC1Af2d4c02E9e2d03fF3b492A09d168124')

_SOURCE_TOKEN = BlockchainAddress('0x57FeAEC5F8f3A19264d8DfF24a88dA9F774e30a2')

_DESTINATION_TOKEN = BlockchainAddress(
    '0x49716ea49473c8B1164d2F503e50319D629CFFC6')

_AMOUNT = 100

_NONCE = 11111

_SIGNER_ADDRESSES = [
    BlockchainAddress('0xBb608811Bfc5fc3444863BC589C7e5F50DF1936a')
]

_SIGNATURES = [
    hexbytes.HexBytes(
        '665b95365f0724784d5c2792ca870ff4bf08b06590ac068f6f89ae7edf640bdd3'
        'aaa116b69b2e0927a3151de498f5f0131beafbadb6c12c1756baa532d931fa81c')
]

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


@pytest.fixture(scope='module')
def source_transaction_id():
    return _TRANSACTION_HASH


@pytest.fixture(scope='module')
def block_number():
    return _BLOCK_NUMBER


@pytest.fixture(scope='module')
def transaction_hash():
    return _TRANSACTION_HASH


@pytest.fixture(scope='module')
def source_transfer_id():
    return _SOURCE_TRANSFER_ID


@pytest.fixture(scope='module')
def destination_transfer_id():
    return _DESTINATION_TRANSFER_ID


@pytest.fixture(scope='module')
def sender():
    return _SENDER


@pytest.fixture(scope='module')
def recipient():
    return _RECIPIENT


@pytest.fixture(scope='module')
def source_token():
    return _SOURCE_TOKEN


@pytest.fixture(scope='module')
def destination_token():
    return _DESTINATION_TOKEN


@pytest.fixture(scope='module')
def amount():
    return _AMOUNT


@pytest.fixture(scope='module')
def nonce():
    return _NONCE


@pytest.fixture(scope='module')
def signer_addresses():
    return _SIGNER_ADDRESSES


@pytest.fixture(scope='module')
def signatures():
    return _SIGNATURES


@pytest.fixture(scope='function')
def transfer_to_event(request):
    return {
        'blockNumber': _BLOCK_NUMBER,
        'transactionHash': _TRANSACTION_HASH,
        'args': {
            'sourceBlockchainId': request.param.value,
            'sourceTransactionId': _TRANSACTION_HASH,
            'sourceTransferId': _SOURCE_TRANSFER_ID,
            'destinationTransferId': _DESTINATION_TRANSFER_ID,
            'sender': _SENDER,
            'recipient': _RECIPIENT,
            'sourceToken': _SOURCE_TOKEN,
            'destinationToken': _DESTINATION_TOKEN,
            'amount': _AMOUNT,
            'nonce': _NONCE,
            'signerAddresses': _SIGNER_ADDRESSES,
            'signatures': _SIGNATURES
        }
    }
