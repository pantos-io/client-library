import unittest.mock

import pytest
from pantos.common.blockchains.base import Blockchain

from pantos.client.library.blockchains.ethereum import EthereumClient
from pantos.client.library.blockchains.ethereum import EthereumClientError
from pantos.client.library.blockchains.ethereum import UnknownTransferError


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
@unittest.mock.patch.object(
    EthereumClient, '_create_hub_contract',
    return_value=MockedHubContract([False, 'data1', 'data2', 'data3']))
def test_read_service_node_url_error_service_node_inactive(
        mocked_hub_contract, mocked_utilities, ethereum_client,
        service_node_1):
    with pytest.raises(EthereumClientError):
        ethereum_client.read_service_node_url(str(service_node_1))


@unittest.mock.patch.object(EthereumClient, '_get_utilities',
                            return_value=MockedUtilities())
@unittest.mock.patch.object(
    EthereumClient, '_create_hub_contract',
    return_value=MockedHubContract([False, 'data1', 'data2']))
def test_read_service_node_url_error(mocked_hub_contract, mocked_utilities,
                                     ethereum_client, service_node_1):
    with pytest.raises(Exception):
        ethereum_client.read_service_node_url(str(service_node_1))


@unittest.mock.patch.object(EthereumClient, '_get_utilities',
                            return_value=MockedUtilities())
@unittest.mock.patch.object(
    EthereumClient, '_create_hub_contract', return_value=MockedHubContract(
        [True, 'service_node_url', 'data2', 'data3', 'data4', 'data5']))
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


@pytest.mark.parametrize('transfer_to_event',
                         [blockchain for blockchain in Blockchain],
                         indirect=True)
@unittest.mock.patch.object(EthereumClient, '_get_utilities')
@unittest.mock.patch.object(EthereumClient, '_get_config')
@unittest.mock.patch.object(EthereumClient, '_create_hub_contract')
def test_read_destination_transfer_correct(
        mocked_hub_contract, mocked_get_config, mocked_get_utilities,
        transfer_to_event, ethereum_client, source_transaction_id,
        block_number, transaction_hash, source_transfer_id,
        destination_transfer_id, sender, recipient, source_token,
        destination_token, amount, nonce, signer_addresses, signatures):
    mocked_get_utilities().create_node_connections().\
        eth.get_block_number().get_minimum_result.return_value = 1000
    mocked_get_config().__getitem__.return_value = 5
    expected_response = EthereumClient.DestinationTransferResponse(
        1000, block_number, transaction_hash.hex(), source_transfer_id,
        destination_transfer_id, sender, recipient, source_token,
        destination_token, amount, nonce, signer_addresses,
        [signature.hex() for signature in signatures])
    mocked_get_utilities().get_logs.return_value = [transfer_to_event]
    request = EthereumClient.DestinationTransferRequest(
        transfer_to_event['args']['sourceBlockchainId'], source_transaction_id)

    transfer_response = ethereum_client.read_destination_transfer(request)

    assert expected_response == transfer_response


@pytest.mark.parametrize('blocks_queried_expected', [{
    'blocks_to_search': 10,
    'last_block_number': 20,
    'blocks_per_query': 5,
    'expected': [(16, 20), (11, 15)]
}, {
    'blocks_to_search': 5,
    'last_block_number': 15,
    'blocks_per_query': 1,
    'expected': [(15, 15), (14, 14), (13, 13), (12, 12), (11, 11)]
}, {
    'blocks_to_search': 10,
    'last_block_number': 20,
    'blocks_per_query': 15,
    'expected': [(11, 20)]
}, {
    'blocks_to_search': 10,
    'last_block_number': 20,
    'blocks_per_query': 7,
    'expected': [(14, 20), (11, 13)]
}, {
    'blocks_to_search': 1,
    'last_block_number': 15,
    'blocks_per_query': 5,
    'expected': [(15, 15)]
}])
@unittest.mock.patch.object(EthereumClient, '_get_utilities')
@unittest.mock.patch.object(EthereumClient, '_get_config')
@unittest.mock.patch.object(EthereumClient, '_create_hub_contract')
def test_read_destination_transfer_correct_blocks_queried(
        mocked_hub_contract, mocked_get_config, mocked_get_utilities,
        blocks_queried_expected, ethereum_client):
    mocked_get_utilities().create_node_connections().\
        eth.get_block_number().get_minimum_result.return_value = \
        blocks_queried_expected['last_block_number']
    mocked_get_config().__getitem__.return_value = \
        blocks_queried_expected['blocks_per_query']
    mocked_get_utilities().get_logs.return_value = []
    request = EthereumClient.DestinationTransferRequest(
        Blockchain.ETHEREUM, '0x0',
        blocks_queried_expected['blocks_to_search'])

    with pytest.raises(UnknownTransferError):
        ethereum_client.read_destination_transfer(request)

    get_logs_blocks_queried = []
    for call_args in mocked_get_utilities().get_logs.call_args_list:
        get_logs_blocks_queried.append((call_args[0][1], call_args[0][2]))

    assert blocks_queried_expected['expected'] == get_logs_blocks_queried


@unittest.mock.patch.object(EthereumClient, '_get_utilities')
@unittest.mock.patch.object(EthereumClient, '_get_config')
@unittest.mock.patch.object(EthereumClient, '_create_hub_contract')
def test_read_destination_transfer_unkown_transfer(mocked_hub_contract,
                                                   mocked_get_config,
                                                   mocked_get_utilities,
                                                   ethereum_client):
    mocked_get_utilities().create_node_connections().eth.get_block_number(
    ).get_minimum_result.return_value = 1000
    mocked_get_config().__getitem__.return_value = 5
    mocked_get_utilities().get_logs.return_value = []

    request = EthereumClient.DestinationTransferRequest(
        Blockchain.ETHEREUM, '0x0')

    with pytest.raises(UnknownTransferError):
        ethereum_client.read_destination_transfer(request)


@unittest.mock.patch.object(EthereumClient, '_get_utilities',
                            side_effect=Exception)
def test_read_destination_transfer_error(mocked_get_utilities,
                                         ethereum_client):
    request = EthereumClient.DestinationTransferRequest(
        Blockchain.ETHEREUM, '0x0')

    with pytest.raises(EthereumClientError):
        ethereum_client.read_destination_transfer(request)
