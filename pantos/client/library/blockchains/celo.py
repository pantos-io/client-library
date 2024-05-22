"""Module for Celo-specific clients and errors. Since Celo is
Ethereum-compatible, the client implementation inherits from the
pantos.client.library.blockchains.ethereum module.

"""
from pantos.common.blockchains.base import Blockchain

from pantos.client.library.blockchains import BlockchainClientError
from pantos.client.library.blockchains.ethereum import EthereumClient
from pantos.client.library.blockchains.ethereum import EthereumClientError


class CeloClientError(EthereumClientError):
    """Exception class for all Celo client errors.

    """
    pass


class CeloClient(EthereumClient):
    """Celo-specific blockchain client.

    """
    @classmethod
    def get_blockchain(cls) -> Blockchain:
        # Docstring inherited
        return Blockchain.CELO

    @classmethod
    def get_error_class(cls) -> type[BlockchainClientError]:
        # Docstring inherited
        return CeloClientError
