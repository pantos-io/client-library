import contextlib
import unittest

import pytest
from pantos.common.blockchains.base import Blockchain
from pantos.common.servicenodes import ServiceNodeClient

from pantos.client.library.business.bids import BidInteractor
from pantos.client.library.business.bids import BidInteractorError
from pantos.client.library.business.tokens import TokenInteractor


class _Break(Exception):
    pass


class _MockThread:
    def __init__(self, target):
        self.__target = target

    def start(self):
        self.__target()


class _MockFuture:
    def __init__(self, function, *args):
        try:
            self.__result = function(*args)
        except Exception as error:
            self.__result = error

    def result(self):
        if isinstance(self.__result, Exception):
            raise self.__result
        return self.__result


class _MockThreadPoolExecutor(contextlib.AbstractContextManager):
    def __init__(self):
        pass

    def __exit__(self, *args):
        pass

    def submit(self, function, *args):
        return _MockFuture(function, *args)


def _mock_as_completed(dictionary):
    return dictionary.keys()


@unittest.mock.patch.object(BidInteractor, 'retrieve_service_node_bids')
def test_find_cheapest_service_node_bid_correct(
        mocked_retrieve_service_node_bids, service_node_1, service_node_2,
        bids_1, bids_2):
    mocked_retrieve_service_node_bids.return_value = {
        service_node_1: bids_1,
        service_node_2: bids_2
    }
    bid_interactor = BidInteractor()

    cheapest_service_node_bid = bid_interactor.find_cheapest_service_node_bid(
        Blockchain.CELO, Blockchain.CRONOS)

    assert cheapest_service_node_bid.service_node_address == service_node_1
    assert cheapest_service_node_bid.service_node_bid.fee == 1


@unittest.mock.patch.object(BidInteractor, 'retrieve_service_node_bids')
def test_find_cheapest_service_node_bid_no_bids_error(
        mocked_retrieve_service_node_bids, service_node_1):
    mocked_retrieve_service_node_bids.return_value = {service_node_1: []}
    bid_interactor = BidInteractor()

    with pytest.raises(BidInteractorError):
        bid_interactor.find_cheapest_service_node_bid(Blockchain.CELO,
                                                      Blockchain.CRONOS)


@unittest.mock.patch.object(BidInteractor, 'retrieve_service_node_bids')
def test_find_cheapest_service_node_bid_interactor_error(
        mocked_retrieve_service_node_bids):
    mocked_retrieve_service_node_bids.side_effect = BidInteractorError('')
    bid_interactor = BidInteractor()

    with pytest.raises(BidInteractorError):
        bid_interactor.find_cheapest_service_node_bid(Blockchain.CELO,
                                                      Blockchain.CRONOS)


@unittest.mock.patch.object(BidInteractor, 'retrieve_service_node_bids')
def test_find_cheapest_service_node_bid_error(
        mocked_retrieve_service_node_bids):
    mocked_retrieve_service_node_bids.side_effect = Exception
    bid_interactor = BidInteractor()

    with pytest.raises(BidInteractorError):
        bid_interactor.find_cheapest_service_node_bid(Blockchain.CELO,
                                                      Blockchain.CRONOS)


@unittest.mock.patch('pantos.client.library.business.bids.config',
                     {'service_nodes': {
                         'timeout': 1
                     }})
@unittest.mock.patch('concurrent.futures.as_completed', _mock_as_completed)
@unittest.mock.patch('concurrent.futures.ThreadPoolExecutor',
                     _MockThreadPoolExecutor)
@unittest.mock.patch('threading.Thread', _MockThread)
@unittest.mock.patch.object(TokenInteractor, 'convert_amount_to_main_unit',
                            lambda _0, _1, _2, z: z)
@unittest.mock.patch.object(ServiceNodeClient, 'bids')
@unittest.mock.patch('pantos.client.library.business.bids.'
                     'get_blockchain_client')
def test_retrieve_service_node_bids_correct(mocked_get_blockchain_client,
                                            mocked_service_node_bids,
                                            service_node_1, service_node_2,
                                            bids_1):
    mocked_get_blockchain_client().read_service_node_addresses.return_value = [
        service_node_1, service_node_2
    ]
    mocked_get_blockchain_client().read_service_node_url.return_value = ''
    mocked_get_blockchain_client().get_blockchain.return_value = \
        Blockchain.CELO
    mocked_service_node_bids.return_value = bids_1
    bid_interactor = BidInteractor()

    bids = bid_interactor.retrieve_service_node_bids(Blockchain.CELO,
                                                     Blockchain.CRONOS, True)

    assert list(bids.keys()) == [service_node_1, service_node_2]
    assert list(bids.values()) == [bids_1, bids_1]


@unittest.mock.patch('pantos.client.library.business.bids.config',
                     {'service_nodes': {
                         'timeout': 1
                     }})
@unittest.mock.patch('concurrent.futures.as_completed', _mock_as_completed)
@unittest.mock.patch('concurrent.futures.ThreadPoolExecutor',
                     _MockThreadPoolExecutor)
@unittest.mock.patch('threading.Thread', _MockThread)
@unittest.mock.patch.object(ServiceNodeClient, 'bids')
@unittest.mock.patch('pantos.client.library.business.bids.'
                     'get_blockchain_client')
def test_retrieve_service_node_bids_not_fee_in_main_unint_correct(
        mocked_get_blockchain_client, mocked_service_node_bids, service_node_1,
        service_node_2, bids_1):
    mocked_get_blockchain_client().read_service_node_addresses.return_value = [
        service_node_1, service_node_2
    ]
    mocked_get_blockchain_client().read_service_node_url.return_value = ''
    mocked_get_blockchain_client().get_blockchain.return_value = \
        Blockchain.CELO
    mocked_service_node_bids.return_value = bids_1
    bid_interactor = BidInteractor()

    bids = bid_interactor.retrieve_service_node_bids(Blockchain.CELO,
                                                     Blockchain.CRONOS, False)

    assert list(bids.keys()) == [service_node_1, service_node_2]
    assert list(bids.values()) == [bids_1, bids_1]


@unittest.mock.patch('pantos.client.library.business.bids.config',
                     {'service_nodes': {
                         'timeout': 1
                     }})
@unittest.mock.patch('concurrent.futures.as_completed', _mock_as_completed)
@unittest.mock.patch('concurrent.futures.ThreadPoolExecutor',
                     _MockThreadPoolExecutor)
@unittest.mock.patch('threading.Thread', _MockThread)
@unittest.mock.patch.object(TokenInteractor, 'convert_amount_to_main_unit',
                            lambda _0, _1, _2, z: z)
@unittest.mock.patch.object(ServiceNodeClient, 'bids')
@unittest.mock.patch('pantos.client.library.business.bids.'
                     'get_blockchain_client')
def test_retrieve_service_node_bids_unreachable_service_nodes(
        mocked_get_blockchain_client, mocked_service_node_bids, service_node_1,
        service_node_2):
    mocked_get_blockchain_client().read_service_node_addresses.return_value = [
        service_node_1, service_node_2
    ]
    mocked_get_blockchain_client().read_service_node_url.return_value = ''
    mocked_get_blockchain_client().get_blockchain.return_value = \
        Blockchain.CELO
    mocked_service_node_bids.side_effect = Exception
    bid_interactor = BidInteractor()

    bids = bid_interactor.retrieve_service_node_bids(Blockchain.CELO,
                                                     Blockchain.CRONOS, False)

    assert bids == {}


@unittest.mock.patch('pantos.client.library.business.bids.'
                     'get_blockchain_client')
def test_retrieve_service_node_bids_general_error(
        mocked_get_blockchain_client):
    mocked_get_blockchain_client.side_effect = Exception
    bid_interactor = BidInteractor()

    with pytest.raises(BidInteractorError):
        bid_interactor.retrieve_service_node_bids(Blockchain.CELO,
                                                  Blockchain.CRONOS, True)
