"""Business logic for handling service node bids.

"""
import concurrent.futures
import dataclasses
import itertools
import secrets
import typing

from pantos.common.blockchains.base import Blockchain
from pantos.common.entities import ServiceNodeBid
from pantos.common.servicenodes import ServiceNodeClient
from pantos.common.types import BlockchainAddress

from pantos.client.library.blockchains import get_blockchain_client
from pantos.client.library.blockchains.base import BlockchainClient
from pantos.client.library.business.base import Interactor
from pantos.client.library.business.base import InteractorError
from pantos.client.library.business.tokens import TokenInteractor
from pantos.client.library.configuration import config
from pantos.client.library.constants import TOKEN_SYMBOL_PAN


class BidInteractorError(InteractorError):
    """Exception class for all bid interactor errors.

    """
    pass


class BidInteractor(Interactor):
    """Interactor for handling service node bids.

    """
    @dataclasses.dataclass
    class CheapestServiceNodeBid:
        """Response data for finding the cheapest service node bid.

        Attributes
        ----------
        service_node_address : BlockchainAddress
            The address of the service node with the cheapest bid.
        service_node_bid: ServiceNodeBid
            The service node bid with the lowest fee. If more than one
            service node bid with the lowest fee is found, the one with
            the lower execution time is selected. If they have the same
            execution time, one is chosen randomly.

        """
        service_node_address: BlockchainAddress
        service_node_bid: ServiceNodeBid

    def find_cheapest_service_node_bid(
            self, source_blockchain: Blockchain,
            destination_blockchain: Blockchain) \
            -> CheapestServiceNodeBid:
        """Find the cheapest service node bid.

        Parameters
        ----------
        source_blockchain : Blockchain
            The source blockchain of the service node bid.
        destination_blockchain : Blockchain
            The destination blockchain of the service node bid.

        Returns
        -------
        CheapestServiceNodeBid
            The response data with the cheapest service node bid.

        Raises
        ------
        BidInteractorError
            If the cheapest service node bid cannot be searched for or
            if no active service node bid is found.

        """
        try:
            cheapest_bid_pairs: typing.List[typing.Tuple[BlockchainAddress,
                                                         ServiceNodeBid]] = []
            all_service_node_bids = self.retrieve_service_node_bids(
                source_blockchain, destination_blockchain, False)
            for service_node_address, service_node_bids in \
                    all_service_node_bids.items():
                if len(service_node_bids) == 0:
                    continue
                bid_pairs = cheapest_bid_pairs + list(
                    zip(itertools.repeat(service_node_address),
                        service_node_bids))
                cheapest_bid = min(
                    bid_pairs, key=lambda bid_pair:
                    (bid_pair[1].fee, bid_pair[1].execution_time))[1]
                cheapest_bid_pairs = [
                    bid_pair for bid_pair in bid_pairs
                    if bid_pair[1].fee == cheapest_bid.fee and
                    bid_pair[1].execution_time == cheapest_bid.execution_time
                ]
            if len(cheapest_bid_pairs) == 0:
                raise BidInteractorError('no active service node bids found')

            service_node_address, service_node_bid = (
                cheapest_bid_pairs[0] if len(cheapest_bid_pairs) == 1 else
                secrets.choice(cheapest_bid_pairs))
            return BidInteractor.CheapestServiceNodeBid(
                service_node_address, service_node_bid)
        except BidInteractorError:
            raise
        except Exception:
            raise BidInteractorError(
                'unable to search for the cheapest service node bid',
                source_blockchain=source_blockchain,
                destination_blockchain=destination_blockchain)

    def retrieve_service_node_bids(
            self, source_blockchain: Blockchain,
            destination_blockchain: Blockchain,
            return_fee_in_main_unit: bool) \
            -> typing.Dict[BlockchainAddress, typing.List[ServiceNodeBid]]:
        """Retrieve the service node bids for token transfers from a
        specified source blockchain to a specified destination
        blockchain.

        Parameters
        ----------
        source_blockchain : Blockchain
            The source blockchain of the service node bids.
        destination_blockchain : Blockchain
            The destination blockchain of the service node bids.
        return_fee_in_main_unit : bool
            True if the service node bids' fee is to be returned in the
            Pantos Token's main unit, False if it is to be returned in
            the Pantos Token's smallest subunit.

        Returns
        -------
        dict of BlockchainAddress and list of ServiceNodeBid
            The matching service node bids of each registered service
            node.

        Raises
        ------
        BidInteractorError
            If the service node bids cannot be retrieved.

        """
        try:
            all_service_node_bids: typing.Dict[
                BlockchainAddress, typing.List[ServiceNodeBid]] = {}
            source_blockchain_client = get_blockchain_client(source_blockchain)
            service_node_addresses = \
                source_blockchain_client.read_service_node_addresses()
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future_to_service_node_address = {
                    executor.submit(
                        self.__retrieve_bid_from_service_node,  # yapf bug
                        source_blockchain_client,
                        destination_blockchain,
                        service_node_address,
                        return_fee_in_main_unit): service_node_address
                    for service_node_address in service_node_addresses
                }
                for future in concurrent.futures.as_completed(
                        future_to_service_node_address):
                    service_node_address = future_to_service_node_address[
                        future]
                    service_node_bids = future.result()
                    if service_node_bids is not None:
                        all_service_node_bids[
                            service_node_address] = service_node_bids
                return all_service_node_bids
        except Exception:
            raise BidInteractorError(
                'unable to retrieve the service node bids',
                source_blockchain=source_blockchain,
                destination_blockchain=destination_blockchain)

    def __retrieve_bid_from_service_node(
            self, source_blockchain_client: BlockchainClient,
            destination_blockchain: Blockchain,
            service_node_address: BlockchainAddress,
            return_fee_in_main_unit: bool) \
            -> typing.Optional[list[ServiceNodeBid]]:
        service_node_url = \
            source_blockchain_client.read_service_node_url(
                service_node_address)
        source_blockchain = source_blockchain_client.get_blockchain()
        timeout = config['service_nodes']['timeout']
        try:
            service_node_bids = ServiceNodeClient().bids(
                service_node_url, source_blockchain, destination_blockchain,
                timeout)
        except Exception:
            return None
        if not return_fee_in_main_unit:
            return service_node_bids
        token_interactor = TokenInteractor()
        for service_node_bid in service_node_bids:
            fee = service_node_bid.fee
            assert isinstance(fee, int)
            service_node_bid.fee = \
                token_interactor.convert_amount_to_main_unit(
                    source_blockchain, TOKEN_SYMBOL_PAN, fee)
        return service_node_bids
