import unittest.mock

import pytest

from pantos.client.library.business.tokens import TokenInteractor
from pantos.client.library.business.tokens import TokenInteractorError
from pantos.common.blockchains.base import Blockchain


class MockedBlockchainClient:
    def __init__(self, value=None):
        self.value = value

    def read_token_decimals(self, token_address):
        return self.value


def test_convert_amount_to_main_unit_error_negative_subunit():
    with pytest.raises(TokenInteractorError):
        TokenInteractor().convert_amount_to_main_unit(Blockchain.ETHEREUM, 2,
                                                      -1)


def test_convert_amount_to_main_unit_correct_zero_subunit():
    assert TokenInteractor().convert_amount_to_main_unit(
        Blockchain.ETHEREUM, 2, 0) == 0


@unittest.mock.patch.object(TokenInteractor,
                            '_TokenInteractor__token_id_to_token_address')
@unittest.mock.patch(
    'pantos.client.library.business.tokens.get_blockchain_client',
    return_value=MockedBlockchainClient(8))
def test_convert_amount_to_main_unit_correct_non_zero_subunit(
        mocked_blockchain_client, mocked_token_id_to_token_address,
        token_address):
    mocked_token_id_to_token_address.return_value = token_address
    assert TokenInteractor().convert_amount_to_main_unit(
        Blockchain.ETHEREUM, 2, 800000000) == 8


@unittest.mock.patch.object(TokenInteractor,
                            '_TokenInteractor__token_id_to_token_address')
@unittest.mock.patch(
    'pantos.client.library.business.tokens.get_blockchain_client',
    return_value=MockedBlockchainClient(-1))
def test_convert_amount_to_main_unit_error(mocked_blockchain_client,
                                           mocked_token_id_to_token_address,
                                           token_address):
    mocked_token_id_to_token_address.return_value = token_address
    with pytest.raises(Exception):
        TokenInteractor().convert_amount_to_main_unit(Blockchain.ETHEREUM, 2,
                                                      800000000)


def test_convert_amount_to_subunit_error_negative_unit():
    with pytest.raises(TokenInteractorError):
        TokenInteractor().convert_amount_to_subunit(Blockchain.ETHEREUM, 2, -1)


def test_convert_amount_to_subunit_correct_zero():
    assert TokenInteractor().convert_amount_to_subunit(Blockchain.ETHEREUM, 2,
                                                       0) == 0


@unittest.mock.patch.object(TokenInteractor,
                            '_TokenInteractor__token_id_to_token_address')
@unittest.mock.patch(
    'pantos.client.library.business.tokens.get_blockchain_client',
    return_value=MockedBlockchainClient(8))
def test_convert_amount_to_subunit_correct_non_zero(
        mocked_blockchain_client, mocked_token_id_to_token_address,
        token_address):
    mocked_token_id_to_token_address.return_value = token_address
    assert TokenInteractor().convert_amount_to_subunit(Blockchain.ETHEREUM, 2,
                                                       8) == 800000000
