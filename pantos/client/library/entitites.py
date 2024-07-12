"""Module that defines the Pantos client library entities.

"""
import dataclasses
import enum
import uuid

from pantos.common.blockchains.enums import Blockchain
from pantos.common.entities import ServiceNodeTransferStatus
from pantos.common.types import BlockchainAddress


class DestinationTransferStatus(enum.IntEnum):
    """Enumeration of the possible destination transfer statuses.

    """
    UNKNOWN = 0
    SUBMITTED = 1
    CONFIRMED = 2


@dataclasses.dataclass
class ServiceNodeTaskInfo:
    """Service node-related information of a token transfer.

    Attributes
    ----------
    task_id : uuid.UUID
        The task ID of the chosen service node for the token
        transfer.
    service_node_address : BlockchainAddress
        The address of the chosen service node for the token
        transfer.

    """
    task_id: uuid.UUID
    service_node_address: BlockchainAddress


@dataclasses.dataclass
class TokenTransferStatus:
    """Data for the status of a token transfer.

    Attributes
    ----------
    destination_blockchain : Blockchain
        The token transfer's destination blockchain.
    source_transfer_status : ServiceNodeTransferStatus
        The status of the token transfer on the source blockchain.
    destination_transfer_status : DestinationTransferStatus
        The status of the token transfer on the destination blockchain.
    source_transaction_id : str or None
        The transaction ID of the token transfer on the source
        blockchain (default: None).
    destination_transaction_id : str or None
        The transaction ID of the token transfer on the destination
        blockchain (default: None).
    source_transfer_id : int or None
        The transfer ID of the token transfer on the source
        blockchain (default: None).
    destination_transfer_id : int or None
        The transfer ID of the token transfer on the destination
        blockchain (default: None).
    sender_address : BlockchainAddress or None
        The address of the sender's account on the source blockchain
        (default: None).
    recipient_address : BlockchainAddress or None
        The address of the recipient's account on the destination
        blockchain (default: None).
    source_token_address : BlockchainAddress or None
        The address of the token on the source blockchain (default:
        None).
    destination_token_address : BlockchainAddress or None
        The address of the token on the destination blockchain
        (default: None).
    amount : int or None
        The amount of tokens transferred (default: None).
    validator_nonce : int or None
        The validator nonce of the token transfer (default: None).
    signer_addresses : list[BlockchainAddress] or None
        The addresses of the signers of the token transfer (default:
        None).
    signatures : list[str] or None
        The signatures of the token transfer (default: None).

    """
    destination_blockchain: Blockchain
    source_transfer_status: ServiceNodeTransferStatus
    destination_transfer_status: DestinationTransferStatus
    source_transaction_id: str | None = None
    destination_transaction_id: str | None = None
    source_transfer_id: int | None = None
    destination_transfer_id: int | None = None
    sender_address: BlockchainAddress | None = None
    recipient_address: BlockchainAddress | None = None
    source_token_address: BlockchainAddress | None = None
    destination_token_address: BlockchainAddress | None = None
    amount: int | None = None
    validator_nonce: int | None = None
    signer_addresses: list[BlockchainAddress] | None = None
    signatures: list[str] | None = None
