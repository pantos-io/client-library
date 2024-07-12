"""Business logic for handling Pantos token transfers.

"""
import dataclasses
import math
import time
import typing
import uuid

from pantos.common.blockchains.base import Blockchain
from pantos.common.entities import BlockchainAddressBidPair
from pantos.common.entities import ServiceNodeBid
from pantos.common.entities import ServiceNodeTransferStatus
from pantos.common.servicenodes import ServiceNodeClient
from pantos.common.types import Amount
from pantos.common.types import BlockchainAddress
from pantos.common.types import PrivateKey
from pantos.common.types import TokenId

from pantos.client.library.blockchains import BlockchainClient
from pantos.client.library.blockchains import get_blockchain_client
from pantos.client.library.blockchains.base import UnknownTransferError
from pantos.client.library.business.base import Interactor
from pantos.client.library.business.base import InteractorError
from pantos.client.library.business.bids import BidInteractor
from pantos.client.library.business.tokens import TokenInteractor
from pantos.client.library.configuration import get_blockchain_config
from pantos.client.library.entitites import DestinationTransferStatus
from pantos.client.library.entitites import ServiceNodeTaskInfo
from pantos.client.library.entitites import TokenTransferStatus

_DEFAULT_VALID_UNTIL_BUFFER = 120
"""Default "valid until" timestamp buffer for a token transfer in seconds."""


class TransferInteractorError(InteractorError):
    """Exception class for all transfer interactor errors.

    """
    pass


class TransferInteractor(Interactor):
    """Interactor for handling Pantos token transfers.

    """
    @dataclasses.dataclass
    class TokenTransferStatusRequest:
        """Request data for the status of a token transfer.

        Attributes
        ----------
        source_blockchain : Blockchain
            The token transfer's source blockchain.
        service_node_address : BlockchainAddress
            The address of the service node that is processing the
            token transfer.
        service_node_task_id : uuid.UUID
            The service node task ID of the token transfer.
        blocks_to_search : int or None
            The number of blocks to search for the token transfer
            (default: None).

        """
        source_blockchain: Blockchain
        service_node_address: BlockchainAddress
        service_node_task_id: uuid.UUID
        blocks_to_search: int | None = None

    @dataclasses.dataclass
    class TransferTokensRequest:
        """Request data for a new token transfer.

        Attributes
        ----------
        source_blockchain : Blockchain
            The token transfer's source blockchain.
        destination_blockchain : Blockchain
            The token transfer's destination blockchain.
        sender_private_key : PrivateKey
            The unencrypted private key of the sender's account on the
            source blockchain.
        recipient_address : BlockchainAddress
            The address of the recipient's account on the destination
            blockchain.
        source_token_id : TokenId
            The identifier of the token to be transferred (on the source
            blockchain).
        token_amount : Amount
            The amount of tokens to be transferred (an integer value in
            case of the token's smallest subunit, a decimal value in
            case of the token's main unit).
        service_node_bid : BlockchainAddressBidPair or None
            A pair of the address of the chosen service node and the
            service node's chosen bid.
            If none is specified, the cheapest registered service node
            bid for the token transfer is automatically chosen.
        valid_until_buffer : int
            The buffer in seconds added to the current timestamp plus
            the chosen service node bid's execution time.

        """
        source_blockchain: Blockchain
        destination_blockchain: Blockchain
        sender_private_key: PrivateKey
        recipient_address: BlockchainAddress
        source_token_id: TokenId
        token_amount: Amount
        service_node_bid: typing.Optional[BlockchainAddressBidPair] = None
        valid_until_buffer: int = _DEFAULT_VALID_UNTIL_BUFFER

    def transfer_tokens(self,
                        request: TransferTokensRequest) -> ServiceNodeTaskInfo:
        """Transfer tokens from a sender's account on a source
        blockchain to a recipient's account on a (possibly different)
        destination blockchain.

        Parameters
        ----------
        request : TransferTokensRequest
            The request data for a new token transfer.

        Returns
        -------
        ServiceNodeTaskInfo
            Service node-related information of a token transfer.

        Raises
        ------
        TransferInteractorError
            If the token transfer cannot be executed.

        """
        try:
            find_token_addresses_response = \
                TokenInteractor().find_token_addresses(
                    request.source_blockchain, request.destination_blockchain,
                    request.source_token_id)
            token_amount = self.__compute_token_amount(
                request, find_token_addresses_response.source_token_address)
            service_node_address, service_node_bid = \
                self.__retrieve_service_node_bid(request)
            valid_until = self.__compute_valid_until(request, service_node_bid)
            self.__validate_recipient_address(request)
            source_blockchain_client = get_blockchain_client(
                request.source_blockchain)
            if request.source_blockchain is request.destination_blockchain:
                # Single-chain token transfer
                compute_transfer_signature_request = \
                    BlockchainClient.ComputeTransferSignatureRequest(
                        request.sender_private_key, request.recipient_address,
                        find_token_addresses_response.source_token_address,
                        token_amount, service_node_address, service_node_bid,
                        valid_until)
                compute_transfer_signature_response = \
                    source_blockchain_client.compute_transfer_signature(
                        compute_transfer_signature_request)
                sender_address = \
                    compute_transfer_signature_response.sender_address
                sender_nonce = compute_transfer_signature_response.sender_nonce
                signature = compute_transfer_signature_response.signature
            else:
                # Cross-chain token transfer
                compute_transfer_from_signature_request = \
                    BlockchainClient.ComputeTransferFromSignatureRequest(
                        request.destination_blockchain,
                        request.sender_private_key, request.recipient_address,
                        find_token_addresses_response.source_token_address,
                        find_token_addresses_response.destination_token_address,    # noqa: E501
                        token_amount, service_node_address, service_node_bid,
                        valid_until)
                compute_transfer_from_signature_response = \
                    source_blockchain_client.compute_transfer_from_signature(
                        compute_transfer_from_signature_request)
                sender_address = \
                    compute_transfer_from_signature_response.sender_address
                sender_nonce = \
                    compute_transfer_from_signature_response.sender_nonce
                signature = compute_transfer_from_signature_response.signature
            service_node_url = source_blockchain_client.read_service_node_url(
                service_node_address)
            submit_transfer_request = ServiceNodeClient.SubmitTransferRequest(
                service_node_url, request.source_blockchain,
                request.destination_blockchain, sender_address,
                request.recipient_address,
                find_token_addresses_response.source_token_address,
                find_token_addresses_response.destination_token_address,
                token_amount, service_node_bid, sender_nonce, valid_until,
                signature)
            service_node_task_id = ServiceNodeClient().submit_transfer(
                submit_transfer_request)
            return ServiceNodeTaskInfo(service_node_task_id,
                                       service_node_address)
        except TransferInteractorError:
            raise
        except Exception:
            raise TransferInteractorError('unable to execute a token transfer',
                                          request=request)

    def get_token_transfer_status(self, request: TokenTransferStatusRequest) \
            -> TokenTransferStatus:
        """Get the status of a token transfer.

        Parameters
        ----------
        request : TokenTransferStatusRequest
            The request data for the status of a token transfer.

        Returns
        -------
        TokenTransferStatus
            The data of the token transfer status.

        Raises
        ------
        TransferInteractorError
            If the token transfer status cannot be retrieved.

        """
        try:
            service_node_url = get_blockchain_client(
                request.source_blockchain).read_service_node_url(
                    request.service_node_address)
            source_status = ServiceNodeClient().status(
                service_node_url, request.service_node_task_id)
            token_transfer_status = \
                self.__create_token_transfer_status_response(source_status)
            if source_status.status is not ServiceNodeTransferStatus.CONFIRMED:
                return token_transfer_status
            source_transaction_id = source_status.transaction_id
            token_transfer_status.source_transaction_id = source_transaction_id
            token_transfer_status.source_transfer_id = \
                source_status.transfer_id
            destination_transfer_request = \
                BlockchainClient.DestinationTransferRequest(
                    request.source_blockchain, source_transaction_id)
            try:
                destination_response = get_blockchain_client(
                    source_status.destination_blockchain
                ).read_destination_transfer(destination_transfer_request)
            except UnknownTransferError:
                return token_transfer_status
            token_transfer_status.destination_transfer_status = \
                self.__get_destination_transfer_status(
                    destination_response.latest_block_number,
                    destination_response.transaction_block_number,
                    source_status.destination_blockchain)
            token_transfer_status.destination_transaction_id = \
                destination_response.destination_transaction_id
            token_transfer_status.destination_transfer_id = \
                destination_response.destination_transfer_id
            token_transfer_status.validator_nonce = \
                destination_response.validator_nonce
            token_transfer_status.signer_addresses = \
                destination_response.signer_addresses
            token_transfer_status.signatures = destination_response.signatures
            return token_transfer_status
        except Exception:
            raise TransferInteractorError(
                'unable to get token transfer status', request=request)

    def __compute_token_amount(self, request: TransferTokensRequest,
                               source_token_address: BlockchainAddress) -> int:
        if isinstance(request.token_amount, int):
            return request.token_amount
        return TokenInteractor().convert_amount_to_subunit(
            request.source_blockchain, source_token_address,
            request.token_amount)

    def __compute_valid_until(self, request: TransferTokensRequest,
                              service_node_bid: ServiceNodeBid) -> int:
        if request.valid_until_buffer < 0:
            raise TransferInteractorError(
                '"valid until" buffer must be non-negative',
                valid_until_buffer=request.valid_until_buffer)
        return (math.ceil(time.time()) + service_node_bid.execution_time +
                request.valid_until_buffer)

    def __retrieve_service_node_bid(
            self, request: TransferTokensRequest) \
            -> typing.Tuple[BlockchainAddress, ServiceNodeBid]:
        if request.service_node_bid is None:
            find_cheapest_bid_response = \
                BidInteractor().find_cheapest_service_node_bid(
                    request.source_blockchain, request.destination_blockchain)
            service_node_address = \
                find_cheapest_bid_response.service_node_address
            service_node_bid = find_cheapest_bid_response.service_node_bid
        else:
            service_node_address = request.service_node_bid[0]
            service_node_bid = request.service_node_bid[1]
        return service_node_address, service_node_bid

    def __validate_recipient_address(self, request: TransferTokensRequest):
        recipient_address = request.recipient_address
        source_blockchain_client = get_blockchain_client(
            request.source_blockchain)
        if not source_blockchain_client.is_valid_recipient_address(
                recipient_address):
            raise TransferInteractorError('invalid recipient address',
                                          recipient_address=recipient_address)

    def __create_token_transfer_status_response(
            self,
            transfer_status: ServiceNodeClient.TransferStatusResponse) \
            -> TokenTransferStatus:
        return TokenTransferStatus(
            destination_blockchain=transfer_status.destination_blockchain,
            source_transfer_status=transfer_status.status,
            destination_transfer_status=DestinationTransferStatus.UNKNOWN,
            sender_address=transfer_status.sender_address,
            recipient_address=transfer_status.recipient_address,
            source_token_address=transfer_status.source_token_address,
            destination_token_address=transfer_status.
            destination_token_address, amount=transfer_status.token_amount)

    def __get_destination_transfer_status(
            self, latest_block_number: int, transaction_block_number: int,
            blockchain: Blockchain) -> DestinationTransferStatus:
        confirmations = get_blockchain_config(blockchain)['confirmations']
        if latest_block_number - transaction_block_number < confirmations:
            return DestinationTransferStatus.SUBMITTED
        return DestinationTransferStatus.CONFIRMED
