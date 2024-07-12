import itertools
import unittest.mock

import pytest
from pantos.common.blockchains.base import Blockchain
from pantos.common.entities import ServiceNodeTransferStatus
from pantos.common.servicenodes import ServiceNodeClient
from pantos.common.types import PrivateKey

from pantos.client import BlockchainAddress
from pantos.client.library.blockchains.base import UnknownTransferError
from pantos.client.library.business.tokens import TokenInteractorError
from pantos.client.library.business.transfers import TransferInteractor
from pantos.client.library.business.transfers import TransferInteractorError
from pantos.client.library.entitites import DestinationTransferStatus
from pantos.client.library.entitites import TokenTransferStatus


@unittest.mock.patch(
    'pantos.client.library.business.transfers.TokenInteractor.'
    'find_token_addresses',
    side_effect=TokenInteractorError('unable to search for token addresses'))
def test_transfer_tokens(mocked_find_token_addresses):
    transfer_token_request = TransferInteractor.TransferTokensRequest(
        Blockchain.ETHEREUM, Blockchain.ETHEREUM, PrivateKey('some_key'),
        BlockchainAddress('0xaAE34Ec313A97265635B8496468928549cdd4AB7'),
        BlockchainAddress('0xaAE34Ec313A97265635B8496468928549cdd4AB7'), 10,
        (BlockchainAddress('0xaAE34Ec313A97265635B8496468928549cdd4AB7'), 0),
        10)

    with pytest.raises(TransferInteractorError):
        TransferInteractor().transfer_tokens(transfer_token_request)


@pytest.mark.parametrize('service_node_status',
                         [[source_blockchain, destination_blockchain]
                          for source_blockchain, destination_blockchain in
                          itertools.product(Blockchain, repeat=2)],
                         indirect=True)
@unittest.mock.patch.object(ServiceNodeClient, 'status')
@unittest.mock.patch('pantos.client.library.business.transfers.'
                     'get_blockchain_client')
def test_get_token_transfer_status_unconfirmed_source_correct(
        mocked_blockchain_client, mocked_sn_status, service_node_status,
        service_node_url, service_node_1, task_uuid):
    mocked_blockchain_client().read_service_node_url.return_value = \
        service_node_url
    mocked_sn_status.return_value = service_node_status
    expected_response = _create_minimal_expected_token_transfer_status(
        service_node_status)
    request = TransferInteractor.TokenTransferStatusRequest(
        service_node_status.source_blockchain, service_node_1, task_uuid)

    response = TransferInteractor().get_token_transfer_status(request)

    assert expected_response == response


@pytest.mark.parametrize('service_node_status',
                         [[source_blockchain, destination_blockchain]
                          for source_blockchain, destination_blockchain in
                          itertools.product(Blockchain, repeat=2)],
                         indirect=True)
@unittest.mock.patch.object(ServiceNodeClient, 'status')
@unittest.mock.patch('pantos.client.library.business.transfers.'
                     'get_blockchain_client')
def test_get_token_transfer_status_confirmed_source_unknown_destination(
        mocked_blockchain_client, mocked_sn_status, service_node_status,
        service_node_url, service_node_1, task_uuid):
    mocked_blockchain_client().read_service_node_url.return_value = \
        service_node_url
    mocked_blockchain_client().read_destination_transfer.side_effect = \
        UnknownTransferError()
    service_node_status.status = ServiceNodeTransferStatus.CONFIRMED
    mocked_sn_status.return_value = service_node_status
    expected_response = _create_minimal_expected_token_transfer_status(
        service_node_status)
    expected_response.source_transfer_id = service_node_status.transfer_id
    expected_response.source_transaction_id = \
        service_node_status.transaction_id
    request = TransferInteractor.TokenTransferStatusRequest(
        service_node_status.source_blockchain, service_node_1, task_uuid)

    response = TransferInteractor().get_token_transfer_status(request)

    assert expected_response == response


@pytest.mark.parametrize('service_node_status',
                         [[source_blockchain, destination_blockchain]
                          for source_blockchain, destination_blockchain in
                          itertools.product(Blockchain, repeat=2)],
                         indirect=True)
@unittest.mock.patch.object(ServiceNodeClient, 'status')
@unittest.mock.patch('pantos.client.library.business.transfers.'
                     'get_blockchain_config')
@unittest.mock.patch('pantos.client.library.business.transfers.'
                     'get_blockchain_client')
def test_get_token_transfer_status_confirmed_source_confirmed_destination(
        mocked_blockchain_client, mocked_blockchain_config, mocked_sn_status,
        service_node_status, destination_transfer_response, service_node_url,
        service_node_1, task_uuid):
    mocked_blockchain_client().read_service_node_url.return_value = \
        service_node_url
    mocked_blockchain_client().read_destination_transfer.return_value = \
        destination_transfer_response
    mocked_blockchain_config().__getitem__.return_value = (
        destination_transfer_response.latest_block_number -
        destination_transfer_response.transaction_block_number - 1)
    service_node_status.status = ServiceNodeTransferStatus.CONFIRMED
    mocked_sn_status.return_value = service_node_status
    expected_response = _create_minimal_expected_token_transfer_status(
        service_node_status)
    expected_response.source_transfer_id = service_node_status.transfer_id
    expected_response.source_transaction_id = \
        service_node_status.transaction_id
    expected_response.destination_transfer_status = \
        DestinationTransferStatus.CONFIRMED
    expected_response.destination_transaction_id = \
        destination_transfer_response.destination_transaction_id
    expected_response.destination_transfer_id = \
        destination_transfer_response.destination_transfer_id
    expected_response.validator_nonce = \
        destination_transfer_response.validator_nonce
    expected_response.signer_addresses = \
        destination_transfer_response.signer_addresses
    expected_response.signatures = destination_transfer_response.signatures
    request = TransferInteractor.TokenTransferStatusRequest(
        service_node_status.source_blockchain, service_node_1, task_uuid)

    response = TransferInteractor().get_token_transfer_status(request)

    assert expected_response == response


@pytest.mark.parametrize('service_node_status',
                         [[source_blockchain, destination_blockchain]
                          for source_blockchain, destination_blockchain in
                          itertools.product(Blockchain, repeat=2)],
                         indirect=True)
@unittest.mock.patch.object(ServiceNodeClient, 'status')
@unittest.mock.patch('pantos.client.library.business.transfers.'
                     'get_blockchain_config')
@unittest.mock.patch('pantos.client.library.business.transfers.'
                     'get_blockchain_client')
def test_get_token_transfer_status_confirmed_source_submitted_destination(
        mocked_blockchain_client, mocked_blockchain_config, mocked_sn_status,
        service_node_status, destination_transfer_response, service_node_url,
        service_node_1, task_uuid):
    mocked_blockchain_client().read_service_node_url.return_value = \
        service_node_url
    mocked_blockchain_client().read_destination_transfer.return_value = \
        destination_transfer_response
    mocked_blockchain_config().__getitem__.return_value = (
        destination_transfer_response.latest_block_number -
        destination_transfer_response.transaction_block_number + 1)
    service_node_status.status = ServiceNodeTransferStatus.CONFIRMED
    mocked_sn_status.return_value = service_node_status
    expected_response = _create_minimal_expected_token_transfer_status(
        service_node_status)
    expected_response.source_transfer_id = service_node_status.transfer_id
    expected_response.source_transaction_id = \
        service_node_status.transaction_id
    expected_response.destination_transfer_status = \
        DestinationTransferStatus.SUBMITTED
    expected_response.destination_transaction_id = \
        destination_transfer_response.destination_transaction_id
    expected_response.destination_transfer_id = \
        destination_transfer_response.destination_transfer_id
    expected_response.validator_nonce = \
        destination_transfer_response.validator_nonce
    expected_response.signer_addresses = \
        destination_transfer_response.signer_addresses
    expected_response.signatures = destination_transfer_response.signatures
    request = TransferInteractor.TokenTransferStatusRequest(
        service_node_status.source_blockchain, service_node_1, task_uuid)

    response = TransferInteractor().get_token_transfer_status(request)

    assert expected_response == response


@unittest.mock.patch(
    'pantos.client.library.business.transfers.'
    'get_blockchain_client', side_effet=Exception)
def test_get_token_transfer_status_error(service_node_1, task_uuid):
    request = TransferInteractor.TokenTransferStatusRequest(
        Blockchain.ETHEREUM, service_node_1, task_uuid)
    with pytest.raises(TransferInteractorError):
        TransferInteractor().get_token_transfer_status(request)


def _create_minimal_expected_token_transfer_status(
        service_node_status: ServiceNodeClient.TransferStatusResponse) \
        -> TokenTransferStatus:
    return TokenTransferStatus(
        destination_blockchain=service_node_status.destination_blockchain,
        source_transfer_status=service_node_status.status,
        destination_transfer_status=DestinationTransferStatus.UNKNOWN,
        sender_address=service_node_status.sender_address,
        recipient_address=service_node_status.recipient_address,
        source_token_address=service_node_status.source_token_address,
        destination_token_address=service_node_status.
        destination_token_address, amount=service_node_status.token_amount)
