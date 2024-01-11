import unittest.mock

import pytest

from pantos.client.library.blockchains.ethereum import EthereumClient
from pantos.client.library.blockchains.ethereum import EthereumClientError
from pantos.common.blockchains.base import Blockchain


@pytest.fixture(scope='module')
@unittest.mock.patch.object(EthereumClient, '__init__', lambda self: None)
def ethereum_client():
    return EthereumClient()


class MockedUtilities:
    def create_node_connections(self):
        return None


class Wrapper:
    def __init__(self, value):
        self.value = value

    def get(self):
        return self.value


class MockedHubContract:
    def __init__(self, value=None):
        self.value = value

    def caller(self):
        return self

    def isValidSenderNonce(self, sender_address, sender_nonce):
        return Wrapper(True)

    def getServiceNodeRecord(self, service_node_address):
        return Wrapper(self.value)

    def getExternalTokenRecord(self, token_address, blockchain):
        return Wrapper(self.value)

    def getServiceNodes(self):
        return Wrapper(self.value)


def test_get_blockchain_correct(ethereum_client):
    assert ethereum_client.get_blockchain() is Blockchain.ETHEREUM
    assert EthereumClient.get_blockchain() is Blockchain.ETHEREUM


def test_get_error_class_correct(ethereum_client):
    assert ethereum_client.get_error_class() is EthereumClientError
    assert EthereumClient.get_error_class() is EthereumClientError


def test_is_valid_recipient_address_zero_address(ethereum_client):
    recipient_address = "0x0000000000000000000000000000000000000000"

    is_valid_address = ethereum_client.is_valid_recipient_address(
        recipient_address)
    assert is_valid_address is False


@pytest.mark.parametrize('recipient_address, result', [
    ('0x0000000000000000000000000000000000000001', True),
    ('0x308eF9f94a642A31D9F9eA83f183544027A9742D', True),
    ('0x308ef9f94a642a31d9f9ea83f183544027a9742d', False),
])
def test_is_valid_recipient_address(ethereum_client, recipient_address,
                                    result):

    is_valid_address = ethereum_client.is_valid_recipient_address(
        recipient_address)
    assert is_valid_address is result


@unittest.mock.patch.object(
    EthereumClient, '_account_id_to_account_address',
    return_value='0x308eF9f94a642A31D9F9eA83f183544027A9742D')
@unittest.mock.patch.object(EthereumClient, '_get_config')
@unittest.mock.patch.object(EthereumClient, '_get_utilities',
                            return_value=MockedUtilities())
@unittest.mock.patch.object(EthereumClient, '_create_hub_contract',
                            return_value=MockedHubContract())
@unittest.mock.patch.object(EthereumClient,
                            '_EthereumClient__generate_sender_nonce',
                            return_value=1337)
def test_compute_transfer_signature_correct(
        mocked_sender_nonce, mocked_hub_contract, mocked_utilities,
        mocked_get_config, mocked_account_id_to_account_address,
        ethereum_client, config, transfer_signature_request):
    mocked_get_config.return_value = config
    transfer_signature_response = ethereum_client.compute_transfer_signature(
        transfer_signature_request)
    assert transfer_signature_response.sender_address == \
        mocked_account_id_to_account_address.return_value
    assert transfer_signature_response.sender_nonce == \
        mocked_sender_nonce.return_value


def test_compute_transfer_signature_error(ethereum_client, config,
                                          transfer_signature_request):
    with pytest.raises(Exception):
        ethereum_client.compute_transfer_signature(transfer_signature_request)


@unittest.mock.patch.object(
    EthereumClient, '_account_id_to_account_address',
    return_value='0x308eF9f94a642A31D9F9eA83f183544027A9742D')
@unittest.mock.patch.object(EthereumClient, '_get_config')
@unittest.mock.patch.object(EthereumClient, '_get_utilities',
                            return_value=MockedUtilities())
@unittest.mock.patch.object(EthereumClient, '_create_hub_contract',
                            return_value=MockedHubContract())
@unittest.mock.patch.object(EthereumClient,
                            '_EthereumClient__generate_sender_nonce',
                            return_value=1337)
def test_compute_transfer_from_signature_correct(
        mocked_sender_nonce, mocked_hub_contract, mocked_get_utilities,
        mocked_get_config, mocked_account_id_to_account_address,
        ethereum_client, config, transfer_from_signature_request):
    mocked_get_config.return_value = config
    transfer_from_signature_response = \
        ethereum_client.compute_transfer_from_signature(
            transfer_from_signature_request)
    assert transfer_from_signature_response.sender_address == \
        mocked_account_id_to_account_address.return_value
    assert transfer_from_signature_response.sender_nonce == \
        mocked_sender_nonce.return_value


def test_compute_transfer_from_signature_error(
        ethereum_client, config, transfer_from_signature_request):
    with pytest.raises(Exception):
        ethereum_client.compute_transfer_from_signature(
            transfer_from_signature_request)


@unittest.mock.patch.object(EthereumClient, '_get_utilities',
                            return_value=MockedUtilities())
@unittest.mock.patch.object(EthereumClient, '_create_hub_contract',
                            return_value=MockedHubContract(
                                [False, 'data1', 'data2', 'data3']))
def test_read_service_node_url_error_service_node_inactive(
        mocked_hub_contract, mocked_utilities, ethereum_client,
        service_node_1):
    with pytest.raises(EthereumClientError):
        ethereum_client.read_service_node_url(str(service_node_1))


@unittest.mock.patch.object(EthereumClient, '_get_utilities',
                            return_value=MockedUtilities())
@unittest.mock.patch.object(EthereumClient, '_create_hub_contract',
                            return_value=MockedHubContract(
                                [False, 'data1', 'data2']))
def test_read_service_node_url_error(mocked_hub_contract, mocked_utilities,
                                     ethereum_client, service_node_1):
    with pytest.raises(Exception):
        ethereum_client.read_service_node_url(str(service_node_1))


@unittest.mock.patch.object(EthereumClient, '_get_utilities',
                            return_value=MockedUtilities())
@unittest.mock.patch.object(EthereumClient, '_create_hub_contract',
                            return_value=MockedHubContract(
                                [True, 'service_node_url', 'data2', 'data3']))
def test_read_service_node_url_correct(mocked_hub_contract, mocked_utilities,
                                       ethereum_client, service_node_1):
    assert ethereum_client.read_service_node_url(
        str(service_node_1)) == 'service_node_url'


@unittest.mock.patch.object(EthereumClient, '_get_utilities',
                            return_value=MockedUtilities())
@unittest.mock.patch.object(EthereumClient, '_create_hub_contract',
                            return_value=MockedHubContract([True, 'address']))
def test_read_external_token_address_correct(mocked_hub_contract,
                                             mocked_utilities, ethereum_client,
                                             token_address):
    assert ethereum_client.read_external_token_address(
        token_address, Blockchain.ETHEREUM) == 'address'


@unittest.mock.patch.object(EthereumClient, '_get_utilities',
                            return_value=MockedUtilities())
@unittest.mock.patch.object(EthereumClient, '_create_hub_contract',
                            return_value=MockedHubContract([False, 'address']))
def test_read_external_token_address_error_inactive_token(
        mocked_hub_contract, mocked_utilities, ethereum_client, token_address):
    with pytest.raises(EthereumClientError):
        ethereum_client.read_external_token_address(token_address,
                                                    Blockchain.ETHEREUM)


@unittest.mock.patch.object(EthereumClient, '_get_utilities',
                            return_value=MockedUtilities())
@unittest.mock.patch.object(EthereumClient, '_create_hub_contract',
                            return_value=MockedHubContract([False]))
def test_read_external_token_address_error_incorrect_data_length(
        mocked_hub_contract, mocked_utilities, ethereum_client, token_address):
    with pytest.raises(Exception):
        ethereum_client.read_external_token_address(token_address,
                                                    Blockchain.ETHEREUM)


@unittest.mock.patch.object(EthereumClient, '_get_utilities',
                            return_value=MockedUtilities())
@unittest.mock.patch.object(EthereumClient, '_create_hub_contract')
def test_read_service_nodes_correct(mocked_hub_contract, mocked_utilities,
                                    ethereum_client, service_node_1,
                                    service_node_2):
    mocked_hub_contract.return_value = MockedHubContract(
        [service_node_1, service_node_2])
    assert ethereum_client.read_service_node_addresses() == [
        service_node_1, service_node_2
    ]


def test_read_service_nodes_error(ethereum_client):
    with pytest.raises(Exception):
        ethereum_client.read_service_node_addresses()
