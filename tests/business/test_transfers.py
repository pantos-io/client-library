import unittest.mock

import pytest

from pantos.client import BlockchainAddress
from pantos.client.library.business.tokens import TokenInteractorError
from pantos.client.library.business.transfers import TransferInteractor
from pantos.client.library.business.transfers import TransferInteractorError
from pantos.common.blockchains.base import Blockchain
from pantos.common.types import PrivateKey


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
