"""Shared fixtures for all pantos.client.library package tests.

"""
import uuid

import hexbytes
import pytest
import web3
from pantos.common.blockchains.enums import Blockchain
from pantos.common.entities import ServiceNodeBid
from pantos.common.servicenodes import ServiceNodeClient
from pantos.common.servicenodes import ServiceNodeTransferStatus
from pantos.common.types import BlockchainAddress
from pantos.common.types import PrivateKey

from pantos.client.library.blockchains.base import BlockchainClient
from pantos.client.library.protocol import get_supported_protocol_versions

_BLOCK_NUMBER = 1

_CHAIN_ID = 51797

_HUB_ADDRESS = BlockchainAddress('0x308eF9f94a642A31D9F9eA83f183544027A9742D')

_FORWARDER_ADDRESS = BlockchainAddress(
    '0x308eF9f94a642A31D9F9eA83f183544027A9742D')

_PAN_TOKEN_ADDRESS = BlockchainAddress(
    '0x53bAFF6C5A3F2F578C78eC8e66464C31aF62A7D6')

_SOURCE_BLOCKCHAIN = Blockchain.CELO

_DESTINATION_BLOCKCHAIN = Blockchain.CRONOS

_SOURCE_TRANSACTION_ID = hexbytes.HexBytes(
    '3273482cfbf640bd5a7056fc3fd418275d2537bb49638035e19f2c4ebcf2e3d9')

_DESTINATION_TRANSACTION_ID = hexbytes.HexBytes(
    '3ee10387c030563d137a604f82f1fc397908358acefd57686be03a25343f3514')

_SOURCE_TRANSFER_ID = 2

_DESTINATION_TRANSFER_ID = 3

_SENDER_PRIVATE_KEY = PrivateKey(
    'a8805f56320e79fba15389c0ad3f5a600980533f9bbe97514360d4cabecfdc1e')

_RECIPIENT_ADDRESS = BlockchainAddress(
    '0xDc825BC1Af2d4c02E9e2d03fF3b492A09d168124')

_SOURCE_TOKEN_ADDRESS = BlockchainAddress(
    '0x57FeAEC5F8f3A19264d8DfF24a88dA9F774e30a2')

_DESTINATION_TOKEN_ADDRESS = BlockchainAddress(
    '0x49716ea49473c8B1164d2F503e50319D629CFFC6')

_TOKEN_AMOUNT = 1000 * 10**8

_TRANSFER_FEE = 10 * 10**8

_TRANSFER_VALID_UNTIL = int(2e9)

_TASK_UUID = uuid.UUID('b6b59888-41c2-4555-825f-47ce387d6853')

_SENDER_NONCE = 43550449137048175

_VALIDATOR_NODE_NONCE = 6855003742198118

_VALIDATOR_NODE_ADDRESSES = [
    BlockchainAddress('0xBb608811Bfc5fc3444863BC589C7e5F50DF1936a')
]

_VALIDATOR_NODE_SIGNATURES = [
    hexbytes.HexBytes(
        '665b95365f0724784d5c2792ca870ff4bf08b06590ac068f6f89ae7edf640bdd3'
        'aaa116b69b2e0927a3151de498f5f0131beafbadb6c12c1756baa532d931fa81c')
]

_SERVICE_NODE_URL = 'http://localhost:8080'

_SERVICE_NODE_1 = BlockchainAddress(
    '0x5188287E724140aa3C432dCfE69E00992aF09d09')

_SERVICE_NODE_2 = BlockchainAddress(
    '0xbD5b933785096837103de4a7a25b75b23153EAbE')

_BIDS_1 = [
    ServiceNodeBid(_SOURCE_BLOCKCHAIN, _DESTINATION_BLOCKCHAIN, 100, 10, 100,
                   'sig1'),
    ServiceNodeBid(_SOURCE_BLOCKCHAIN, _DESTINATION_BLOCKCHAIN, 10, 10, 100,
                   'sig2'),
    ServiceNodeBid(_SOURCE_BLOCKCHAIN, _DESTINATION_BLOCKCHAIN, 1000, 10, 100,
                   'sig3'),
    ServiceNodeBid(_SOURCE_BLOCKCHAIN, _DESTINATION_BLOCKCHAIN, 1, 10, 100,
                   'sig4')
]

_BIDS_2 = [
    ServiceNodeBid(_SOURCE_BLOCKCHAIN, _DESTINATION_BLOCKCHAIN, 200, 10, 100,
                   'sig2'),
    ServiceNodeBid(_SOURCE_BLOCKCHAIN, _DESTINATION_BLOCKCHAIN, 20, 10, 100,
                   'sig4'),
    ServiceNodeBid(_SOURCE_BLOCKCHAIN, _DESTINATION_BLOCKCHAIN, 2000, 10, 100,
                   'sig5'),
    ServiceNodeBid(_SOURCE_BLOCKCHAIN, _DESTINATION_BLOCKCHAIN, 2, 10, 100,
                   'sig6')
]


@pytest.fixture(params=get_supported_protocol_versions())
def protocol_version(request):
    return request.param


@pytest.fixture(scope='session')
def chain_id():
    return _CHAIN_ID


@pytest.fixture(scope='session')
def hub_address():
    return _HUB_ADDRESS


@pytest.fixture(scope='session')
def forwarder_address():
    return _FORWARDER_ADDRESS


@pytest.fixture(scope='session')
def pan_token_address():
    return _PAN_TOKEN_ADDRESS


@pytest.fixture(scope='session')
def source_blockchain():
    return _SOURCE_BLOCKCHAIN


@pytest.fixture(scope='session')
def destination_blockchain():
    return _DESTINATION_BLOCKCHAIN


@pytest.fixture(scope='session')
def service_node_url():
    return _SERVICE_NODE_URL


@pytest.fixture(scope='session')
def service_node_1():
    return _SERVICE_NODE_1


@pytest.fixture(scope='session')
def service_node_2():
    return _SERVICE_NODE_2


@pytest.fixture(scope='session')
def bids_1():
    return _BIDS_1


@pytest.fixture(scope='session')
def bids_2():
    return _BIDS_2


@pytest.fixture(scope='session')
def task_uuid():
    return _TASK_UUID


@pytest.fixture(scope='session')
def block_number():
    return _BLOCK_NUMBER


@pytest.fixture(scope='session')
def source_transaction_id():
    return _SOURCE_TRANSACTION_ID


@pytest.fixture(scope='session')
def destination_transaction_id():
    return _DESTINATION_TRANSACTION_ID


@pytest.fixture(scope='session')
def source_transfer_id():
    return _SOURCE_TRANSFER_ID


@pytest.fixture(scope='session')
def destination_transfer_id():
    return _DESTINATION_TRANSFER_ID


@pytest.fixture(scope='session')
def sender_address(sender_private_key):
    return BlockchainAddress(web3.Account.from_key(sender_private_key).address)


@pytest.fixture(scope='session')
def sender_private_key():
    return _SENDER_PRIVATE_KEY


@pytest.fixture(scope='session')
def recipient_address():
    return _RECIPIENT_ADDRESS


@pytest.fixture(scope='session')
def source_token_address():
    return _SOURCE_TOKEN_ADDRESS


@pytest.fixture(scope='session')
def destination_token_address():
    return _DESTINATION_TOKEN_ADDRESS


@pytest.fixture(scope='session')
def token_amount():
    return _TOKEN_AMOUNT


@pytest.fixture(scope='session')
def transfer_fee():
    return _TRANSFER_FEE


@pytest.fixture(scope='session')
def transfer_valid_until():
    return _TRANSFER_VALID_UNTIL


@pytest.fixture(scope='session')
def sender_nonce():
    return _SENDER_NONCE


@pytest.fixture(scope='session')
def validator_node_nonce():
    return _VALIDATOR_NODE_NONCE


@pytest.fixture(scope='session')
def validator_node_addresses():
    return _VALIDATOR_NODE_ADDRESSES


@pytest.fixture(scope='session')
def validator_node_signatures():
    return _VALIDATOR_NODE_SIGNATURES


@pytest.fixture(scope='function')
def service_node_status(request, task_uuid, sender_address, recipient_address,
                        source_token_address, destination_token_address,
                        token_amount, transfer_fee, source_transfer_id,
                        source_transaction_id):
    return ServiceNodeClient.TransferStatusResponse(
        task_uuid, request.param[0], request.param[1], sender_address,
        recipient_address, source_token_address, destination_token_address,
        token_amount, transfer_fee, ServiceNodeTransferStatus.ACCEPTED,
        source_transfer_id, source_transaction_id)


@pytest.fixture(scope='function')
def destination_transfer_response(
        block_number, destination_transaction_id, source_transfer_id,
        destination_transfer_id, sender_address, recipient_address,
        source_token_address, destination_token_address, token_amount,
        validator_node_nonce, validator_node_addresses,
        validator_node_signatures):
    return BlockchainClient.DestinationTransferResponse(
        block_number + 100, block_number, destination_transaction_id,
        source_transfer_id, destination_transfer_id, sender_address,
        recipient_address, source_token_address, destination_token_address,
        token_amount, validator_node_nonce, validator_node_addresses,
        validator_node_signatures)
