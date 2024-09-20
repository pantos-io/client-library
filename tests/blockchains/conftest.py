import pytest

from pantos.client.library.blockchains.base import BlockchainClient
from pantos.client.library.constants import TOKEN_SYMBOL_PAN


@pytest.fixture(scope='session')
def blockchain_config(chain_id, hub_address, forwarder_address,
                      pan_token_address):
    return {
        'chain_id': chain_id,
        'hub': hub_address,
        'forwarder': forwarder_address,
        'tokens': {
            TOKEN_SYMBOL_PAN: pan_token_address
        }
    }


@pytest.fixture(scope='package')
def transfer_signature_request(sender_private_key, recipient_address,
                               source_token_address, token_amount,
                               service_node_1, bids_1, transfer_valid_until):
    return BlockchainClient.ComputeTransferSignatureRequest(
        sender_private_key=sender_private_key,
        recipient_address=recipient_address,
        token_address=source_token_address, token_amount=token_amount,
        service_node_address=service_node_1, service_node_bid=bids_1[0],
        valid_until=transfer_valid_until)


@pytest.fixture(scope='package')
def transfer_from_signature_request(destination_blockchain, sender_private_key,
                                    recipient_address, source_token_address,
                                    destination_token_address, token_amount,
                                    service_node_1, bids_1,
                                    transfer_valid_until):
    return BlockchainClient.ComputeTransferFromSignatureRequest(
        destination_blockchain=destination_blockchain,
        sender_private_key=sender_private_key,
        recipient_address=recipient_address,
        source_token_address=source_token_address,
        destination_token_address=destination_token_address,
        token_amount=token_amount, service_node_address=service_node_1,
        service_node_bid=bids_1[0], valid_until=transfer_valid_until)
