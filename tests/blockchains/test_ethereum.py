import unittest.mock

import eth_account.account
import eth_account.messages
import pytest
from pantos.common.blockchains.base import BlockchainUtilitiesError
from pantos.common.blockchains.enums import Blockchain

from pantos.client.library.blockchains.ethereum import _EIP712_DOMAIN_NAME
from pantos.client.library.blockchains.ethereum import \
    _TRANSFER_FROM_MESSAGE_TYPES
from pantos.client.library.blockchains.ethereum import _TRANSFER_MESSAGE_TYPES
from pantos.client.library.blockchains.ethereum import EthereumClient
from pantos.client.library.blockchains.ethereum import EthereumClientError
from pantos.client.library.blockchains.ethereum import UnknownTransferError


@pytest.fixture
@unittest.mock.patch.object(EthereumClient, '__init__', lambda self: None)
def ethereum_client(protocol_version):
    ethereum_client = EthereumClient()
    ethereum_client.protocol_version = protocol_version
    return ethereum_client


@pytest.fixture
def eip712_domain_data(protocol_version, chain_id, forwarder_address):
    return {
        'name': _EIP712_DOMAIN_NAME,
        'version': str(protocol_version.major),
        'chainId': chain_id,
        'verifyingContract': forwarder_address
    }


@pytest.fixture
def transfer_message_data(transfer_signature_request, sender_address,
                          sender_nonce, hub_address, forwarder_address,
                          pan_token_address):
    return {
        'request': {
            'sender': sender_address,
            'recipient': transfer_signature_request.recipient_address,
            'token': transfer_signature_request.token_address,
            'amount': transfer_signature_request.token_amount,
            'serviceNode': transfer_signature_request.service_node_address,
            'fee': transfer_signature_request.service_node_bid.fee,
            'nonce': sender_nonce,
            'validUntil': transfer_signature_request.valid_until
        },
        'blockchainId': Blockchain.ETHEREUM.value,
        'pantosHub': hub_address,
        'pantosForwarder': forwarder_address,
        'pantosToken': pan_token_address
    }


@pytest.fixture
def transfer_from_message_data(transfer_from_signature_request, sender_address,
                               sender_nonce, hub_address, forwarder_address,
                               pan_token_address):
    return {
        'request': {
            'destinationBlockchainId': transfer_from_signature_request.
            destination_blockchain.value,
            'sender': sender_address,
            'recipient': transfer_from_signature_request.recipient_address,
            'sourceToken': transfer_from_signature_request.
            source_token_address,
            'destinationToken': transfer_from_signature_request.
            destination_token_address,
            'amount': transfer_from_signature_request.token_amount,
            'serviceNode': transfer_from_signature_request.
            service_node_address,
            'fee': transfer_from_signature_request.service_node_bid.fee,
            'nonce': sender_nonce,
            'validUntil': transfer_from_signature_request.valid_until
        },
        'sourceBlockchainId': Blockchain.ETHEREUM.value,
        'pantosHub': hub_address,
        'pantosForwarder': forwarder_address,
        'pantosToken': pan_token_address
    }


@pytest.fixture
def transfer_to_succeeded_event(
        request, block_number, destination_transaction_id,
        destination_transfer_id, source_transfer_id, source_transaction_id,
        sender_address, recipient_address, source_token_address,
        destination_token_address, token_amount, validator_node_nonce,
        validator_node_addresses, validator_node_signatures):
    return {
        'blockNumber': block_number,
        'transactionHash': destination_transaction_id,
        'args': {
            'destinationTransferId': destination_transfer_id,
            'request': {
                'sourceBlockchainId': request.param.value,
                'sourceTransferId': source_transfer_id,
                'sourceTransactionId': source_transaction_id,
                'sender': sender_address,
                'recipient': recipient_address,
                'sourceToken': source_token_address,
                'destinationToken': destination_token_address,
                'amount': token_amount,
                'nonce': validator_node_nonce
            },
            'signerAddresses': validator_node_addresses,
            'signatures': validator_node_signatures
        }
    }


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


@unittest.mock.patch.object(EthereumClient, '_get_utilities')
@unittest.mock.patch.object(EthereumClient, '_get_config')
@unittest.mock.patch.object(EthereumClient, '_create_hub_contract')
@unittest.mock.patch('pantos.client.library.blockchains.ethereum.secrets')
def test_compute_transfer_signature_correct(
        mock_secrets, mock_create_hub_contract, mock_get_config,
        mock_get_utilities, ethereum_client, blockchain_config,
        transfer_signature_request, sender_address, sender_nonce,
        eip712_domain_data, transfer_message_data):
    mock_secrets.randbits.return_value = sender_nonce
    mock_create_hub_contract().caller().isValidSenderNonce().get.\
        side_effect = [False, True]
    mock_get_config.return_value = blockchain_config
    mock_get_utilities().get_address.return_value = sender_address

    response = ethereum_client.compute_transfer_signature(
        transfer_signature_request)

    assert response.sender_address == sender_address
    assert response.sender_nonce == sender_nonce

    signable_message = eth_account.messages.encode_typed_data(
        eip712_domain_data, _TRANSFER_MESSAGE_TYPES, transfer_message_data)
    signer_address = eth_account.account.Account.recover_message(
        signable_message, signature=response.signature)
    assert signer_address == sender_address


@unittest.mock.patch.object(EthereumClient, '_get_utilities')
def test_compute_transfer_signature_node_connection_error(
        mock_get_utilities, ethereum_client, transfer_signature_request,
        sender_address):
    node_connection_error_message = 'node connection error'
    mock_get_utilities().create_node_connections.side_effect = \
        BlockchainUtilitiesError(node_connection_error_message)
    mock_get_utilities().get_address.return_value = sender_address

    with pytest.raises(EthereumClientError) as exception_info:
        ethereum_client.compute_transfer_signature(transfer_signature_request)

    raised_error = exception_info.value
    assert raised_error.details['request'] == transfer_signature_request
    assert isinstance(raised_error.__context__, BlockchainUtilitiesError)
    assert str(raised_error.__context__) == node_connection_error_message


@unittest.mock.patch.object(EthereumClient, '_get_utilities')
@unittest.mock.patch.object(EthereumClient, '_get_config')
@unittest.mock.patch.object(EthereumClient, '_create_hub_contract')
@unittest.mock.patch('pantos.client.library.blockchains.ethereum.secrets')
def test_compute_transfer_from_signature_correct(
        mock_secrets, mock_create_hub_contract, mock_get_config,
        mock_get_utilities, ethereum_client, blockchain_config,
        transfer_from_signature_request, sender_address, sender_nonce,
        eip712_domain_data, transfer_from_message_data):
    mock_secrets.randbits.return_value = sender_nonce
    mock_create_hub_contract().caller().isValidSenderNonce().get.\
        side_effect = [False, True]
    mock_get_config.return_value = blockchain_config
    mock_get_utilities().get_address.return_value = sender_address

    response = ethereum_client.compute_transfer_from_signature(
        transfer_from_signature_request)

    assert response.sender_address == sender_address
    assert response.sender_nonce == sender_nonce

    signable_message = eth_account.messages.encode_typed_data(
        eip712_domain_data, _TRANSFER_FROM_MESSAGE_TYPES,
        transfer_from_message_data)
    signer_address = eth_account.account.Account.recover_message(
        signable_message, signature=response.signature)
    assert signer_address == sender_address


@unittest.mock.patch.object(EthereumClient, '_get_utilities')
def test_compute_transfer_from_signature_node_connection_error(
        mock_get_utilities, ethereum_client, transfer_from_signature_request,
        sender_address):
    node_connection_error_message = 'node connection error'
    mock_get_utilities().create_node_connections.side_effect = \
        BlockchainUtilitiesError(node_connection_error_message)
    mock_get_utilities().get_address.return_value = sender_address

    with pytest.raises(EthereumClientError) as exception_info:
        ethereum_client.compute_transfer_from_signature(
            transfer_from_signature_request)

    raised_error = exception_info.value
    assert raised_error.details['request'] == transfer_from_signature_request
    assert isinstance(raised_error.__context__, BlockchainUtilitiesError)
    assert str(raised_error.__context__) == node_connection_error_message


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
        [True, 'service_node_url', 'data2', 'data3', 'data4']))
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
                                             source_token_address):
    assert ethereum_client.read_external_token_address(
        source_token_address, Blockchain.ETHEREUM) == 'address'


@unittest.mock.patch.object(EthereumClient, '_get_utilities',
                            return_value=MockedUtilities())
@unittest.mock.patch.object(EthereumClient, '_create_hub_contract',
                            return_value=MockedHubContract([False, 'address']))
def test_read_external_token_address_error_inactive_token(
        mocked_hub_contract, mocked_utilities, ethereum_client,
        source_token_address):
    with pytest.raises(EthereumClientError):
        ethereum_client.read_external_token_address(source_token_address,
                                                    Blockchain.ETHEREUM)


@unittest.mock.patch.object(EthereumClient, '_get_utilities',
                            return_value=MockedUtilities())
@unittest.mock.patch.object(EthereumClient, '_create_hub_contract',
                            return_value=MockedHubContract([False]))
def test_read_external_token_address_error_incorrect_data_length(
        mocked_hub_contract, mocked_utilities, ethereum_client,
        source_token_address):
    with pytest.raises(Exception):
        ethereum_client.read_external_token_address(source_token_address,
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


@pytest.mark.parametrize('transfer_to_succeeded_event',
                         [blockchain for blockchain in Blockchain],
                         indirect=True)
@unittest.mock.patch.object(EthereumClient, '_get_utilities')
@unittest.mock.patch.object(EthereumClient, '_get_config')
@unittest.mock.patch.object(EthereumClient, '_create_hub_contract')
def test_read_destination_transfer_correct(
        mocked_hub_contract, mocked_get_config, mocked_get_utilities,
        transfer_to_succeeded_event, ethereum_client, source_transaction_id,
        block_number, destination_transaction_id, source_transfer_id,
        destination_transfer_id, sender_address, recipient_address,
        source_token_address, destination_token_address, token_amount,
        validator_node_nonce, validator_node_addresses,
        validator_node_signatures):
    mocked_get_utilities().create_node_connections().\
        eth.get_block_number().get_minimum_result.return_value = 1000
    mocked_get_config().__getitem__.return_value = 5
    expected_response = EthereumClient.DestinationTransferResponse(
        1000, block_number, destination_transaction_id.to_0x_hex(),
        source_transfer_id, destination_transfer_id, sender_address,
        recipient_address, source_token_address, destination_token_address,
        token_amount, validator_node_nonce, validator_node_addresses,
        [signature.to_0x_hex() for signature in validator_node_signatures])
    mocked_get_utilities().get_logs.return_value = [
        transfer_to_succeeded_event
    ]
    request = EthereumClient.DestinationTransferRequest(
        transfer_to_succeeded_event['args']['request']['sourceBlockchainId'],
        source_transaction_id)

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
