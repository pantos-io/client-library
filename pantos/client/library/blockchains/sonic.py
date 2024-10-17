"""Module for Sonic-specific clients and errors. Since Sonic is
Ethereum-compatible, the client implementation inherits from the
pantos.client.library.blockchains.ethereum module.

Note that Pantos used to support Sonic's predecessor Fantom. This module
was renamed accordingly on 2024-10-17.

"""
from pantos.common.blockchains.base import Blockchain

from pantos.client.library.blockchains import BlockchainClientError
from pantos.client.library.blockchains.ethereum import EthereumClient
from pantos.client.library.blockchains.ethereum import EthereumClientError


class SonicClientError(EthereumClientError):
    """Exception class for all Sonic client errors.

    """
    pass


class SonicClient(EthereumClient):
    """Sonic-specific blockchain client.

    """
    @classmethod
    def get_blockchain(cls) -> Blockchain:
        # Docstring inherited
        return Blockchain.SONIC

    @classmethod
    def get_error_class(cls) -> type[BlockchainClientError]:
        # Docstring inherited
        return SonicClientError
