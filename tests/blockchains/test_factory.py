import unittest.mock

import pytest
from pantos.common.blockchains.base import Blockchain

from pantos.client.library.blockchains.avalanche import AvalancheClient
from pantos.client.library.blockchains.base import BlockchainClient
from pantos.client.library.blockchains.bnbchain import BnbChainClient
from pantos.client.library.blockchains.celo import CeloClient
from pantos.client.library.blockchains.cronos import CronosClient
from pantos.client.library.blockchains.ethereum import EthereumClient
from pantos.client.library.blockchains.factory import _blockchain_clients
from pantos.client.library.blockchains.factory import get_blockchain_client
from pantos.client.library.blockchains.polygon import PolygonClient
from pantos.client.library.blockchains.solana import SolanaClient
from pantos.client.library.blockchains.sonic import SonicClient
from pantos.client.library.protocol import get_supported_protocol_versions


@pytest.fixture(autouse=True)
def clear_blockchain_clients():
    _blockchain_clients.clear()


@pytest.mark.parametrize('protocol_version',
                         [None] + get_supported_protocol_versions())
@pytest.mark.parametrize('blockchain',
                         [blockchain for blockchain in Blockchain])
def test_get_blockchain_client_correct(blockchain, protocol_version):
    blockchain_client_class = _get_blockchain_client_class(blockchain)
    with unittest.mock.patch.object(blockchain_client_class, '__init__',
                                    lambda self, protocol_version_: None):
        blockchain_client = get_blockchain_client(
            blockchain, protocol_version=protocol_version)
        assert isinstance(blockchain_client, BlockchainClient)
        assert isinstance(blockchain_client, blockchain_client_class)


def _get_blockchain_client_class(blockchain):
    if blockchain is Blockchain.AVALANCHE:
        return AvalancheClient
    if blockchain is Blockchain.BNB_CHAIN:
        return BnbChainClient
    if blockchain is Blockchain.CELO:
        return CeloClient
    if blockchain is Blockchain.CRONOS:
        return CronosClient
    if blockchain is Blockchain.ETHEREUM:
        return EthereumClient
    if blockchain is Blockchain.SONIC:
        return SonicClient
    if blockchain is Blockchain.POLYGON:
        return PolygonClient
    if blockchain is Blockchain.SOLANA:
        return SolanaClient
    raise NotImplementedError
