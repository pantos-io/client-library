"""Factory for blockchain clients.

"""
import typing

from pantos.common.blockchains.base import Blockchain

from pantos.client.library.blockchains.base import BlockchainClient

_blockchain_clients: typing.Dict[Blockchain, BlockchainClient] = {}
"""Blockchain-specific client objects."""

_blockchain_client_classes = BlockchainClient.find_subclasses()
"""Blockchain-specific client classes."""


def get_blockchain_client(blockchain: Blockchain) -> BlockchainClient:
    """Factory for blockchain-specific client objects.

    Parameters
    ----------
    blockchain : Blockchain
        The blockchain to get the client instance for.

    Returns
    -------
    BlockchainClient
        A blockchain client instance for the specified blockchain.

    """
    blockchain_client = _blockchain_clients.get(blockchain)
    if blockchain_client is None:
        blockchain_client = _blockchain_client_classes[blockchain]()
        _blockchain_clients[blockchain] = blockchain_client
    return blockchain_client
