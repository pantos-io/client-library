"""Factory for blockchain clients.

"""
import semantic_version  # type: ignore
from pantos.common.blockchains.base import Blockchain

from pantos.client.library.blockchains.base import BlockchainClient
from pantos.client.library.protocol import get_latest_protocol_version
from pantos.client.library.protocol import is_supported_protocol_version

_blockchain_clients: dict[tuple[Blockchain, semantic_version.Version],
                          BlockchainClient] = {}
"""Blockchain-specific client objects."""

_blockchain_client_classes = BlockchainClient.find_subclasses()
"""Blockchain-specific client classes."""


def get_blockchain_client(
        blockchain: Blockchain,
        protocol_version: semantic_version.Version | None = None) \
        -> BlockchainClient:
    """Factory for blockchain-specific client objects.

    Parameters
    ----------
    blockchain : Blockchain
        The blockchain to get the client instance for.
    protocol_version : semantic_version.Version, optional
        The version of the Pantos protocol that the blockchain client
        instance must comply with (default: most recent supported
        version).

    Returns
    -------
    BlockchainClient
        A blockchain client instance for the specified blockchain.

    """
    if protocol_version is None:
        protocol_version = get_latest_protocol_version()
    assert is_supported_protocol_version(protocol_version)
    blockchain_client = _blockchain_clients.get((blockchain, protocol_version))
    if blockchain_client is None:
        blockchain_client = _blockchain_client_classes[blockchain](
            protocol_version)
        _blockchain_clients[(blockchain, protocol_version)] = blockchain_client
    return blockchain_client
