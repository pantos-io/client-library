"""Module that implements the Pantos client library's API which is
exposed to the users of the library.

"""
__all__ = [
    'Blockchain', 'BlockchainAddress', 'PantosClientError', 'PrivateKey',
    'ServiceNodeBid', 'TokenSymbol', 'ServiceNodeTaskInfo',
    'DestinationTransferStatus', 'TokenTransferStatus', 'decrypt_private_key',
    'retrieve_service_node_bids', 'retrieve_token_balance', 'transfer_tokens',
    'get_token_transfer_status', 'deploy_pantos_compatible_token'
]

import uuid as _uuid

from pantos.common.blockchains.base import Blockchain
from pantos.common.entities import \
    BlockchainAddressBidPair as _BlockchainAddressBidPair
from pantos.common.entities import ServiceNodeBid
from pantos.common.types import AccountId as _AccountId
from pantos.common.types import Amount as _Amount
from pantos.common.types import BlockchainAddress
from pantos.common.types import PrivateKey
from pantos.common.types import TokenId as _TokenId
from pantos.common.types import TokenSymbol

from pantos.client.library import initialize_library as _initialize_library
from pantos.client.library.blockchains import \
    get_blockchain_client as _get_blockchain_client
from pantos.client.library.business.bids import BidInteractor as _BidInteractor
from pantos.client.library.business.deployments import \
    TokenDeploymentInteractor as _TokenDeploymentInteractor
from pantos.client.library.business.tokens import \
    TokenInteractor as _TokenInteractor
from pantos.client.library.business.transfers import \
    TransferInteractor as _TransferInteractor
from pantos.client.library.constants import \
    TOKEN_SYMBOL_PAN as _TOKEN_SYMBOL_PAN
from pantos.client.library.entitites import DestinationTransferStatus
from pantos.client.library.entitites import ServiceNodeTaskInfo
from pantos.client.library.entitites import TokenTransferStatus
from pantos.client.library.exceptions import ClientError as _ClientError

# Exception to be used by external client library users
PantosClientError = _ClientError


def decrypt_private_key(blockchain: Blockchain, keystore: str,
                        password: str) -> PrivateKey:
    """Decrypt the private key from a password-encrypted keystore.

    Parameters
    ----------
    blockchain : Blockchain
        The blockchain to load the private key for.
    keystore: str
        The keystore contents.
    password : str
        The password to decrypt the private key.

    Returns
    -------
    PrivateKey
        The decrypted private key.

    Raises
    ------
    PantosClientError
        If the private key cannot be loaded from the keystore file.

    """
    _initialize_library(False)
    return _get_blockchain_client(blockchain).decrypt_private_key(
        keystore, password)


def retrieve_service_node_bids(
        source_blockchain: Blockchain, destination_blockchain: Blockchain,
        return_fee_in_main_unit: bool = True, *, mainnet: bool = False) \
        -> dict[BlockchainAddress, list[ServiceNodeBid]]:
    """Retrieve the service node bids for token transfers from a
    specified source blockchain to a specified destination blockchain.

    Parameters
    ----------
    source_blockchain : Blockchain
        The source blockchain of the service node bids.
    destination_blockchain : Blockchain
        The destination blockchain of the service node bids.
    return_fee_in_main_unit : bool, optional
        True if the service node bids' fee is to be returned in the
        Pantos Token's main unit, False if it is to be returned in the
        Pantos Token's smallest subunit (default: True).
    mainnet : bool, optional
        If True, the function is executed on mainnet. Otherwise, it is
        executed on testnet (default: testnet).

    Returns
    -------
    dict of BlockchainAddress and list of ServiceNodeBid
        The matching service node bids of each registered service
        node.

    Raises
    ------
    PantosClientError
        If the service node bids cannot be retrieved.

    """
    _initialize_library(mainnet)
    return _BidInteractor().retrieve_service_node_bids(
        source_blockchain, destination_blockchain, return_fee_in_main_unit)


def retrieve_token_balance(blockchain: Blockchain, account_id: _AccountId,
                           token_id: _TokenId = _TOKEN_SYMBOL_PAN,
                           return_in_main_unit: bool = True, *,
                           mainnet: bool = False) -> _Amount:
    """Retrieve the token balance of a blockchain account.

    Parameters
    ----------
    blockchain : Blockchain
        The blockchain to retrieve the token balance on.
    account_id : BlockchainAddress or PrivateKey
        The address or unencrypted private key of the blockchain
        account.
    token_id : BlockchainAddress or TokenSymbol
        The address or symbol of the token (default: PAN).
    return_in_main_unit : bool, optional
        True if the token balance is to be returned in the token's main
        unit, False if it is to be returned in the token's smallest
        subunit (default: True).
    mainnet : bool, optional
        If True, the function is executed on mainnet. Otherwise, it is
        executed on testnet (default: testnet).

    Returns
    -------
    int or decimal.Decimal
        The token balance of the blockchain account (an integer value in
        case of the token's smallest subunit, a decimal value in case of
        the token's main unit).

    Raises
    ------
    PantosClientError
        If the token balance cannot be retrieved.

    """
    _initialize_library(mainnet)
    request = _TokenInteractor.RetrieveTokenBalanceRequest(
        blockchain, token_id, account_id, return_in_main_unit)
    return _TokenInteractor().retrieve_token_balance(request)


def transfer_tokens(source_blockchain: Blockchain,
                    destination_blockchain: Blockchain,
                    sender_private_key: PrivateKey,
                    recipient_address: BlockchainAddress,
                    source_token_id: _TokenId, token_amount: _Amount,
                    service_node_bid: _BlockchainAddressBidPair | None = None,
                    *, mainnet: bool = False) -> ServiceNodeTaskInfo:
    """Transfer tokens from a sender's account on a source blockchain to
    a recipient's account on a (possibly different) destination blockchain.

    Parameters
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
    source_token_id : BlockchainAddress or TokenSymbol
        The address or symbol of the token to be transferred (on the
        source blockchain).
    token_amount : int or decimal.Decimal
        The amount of tokens to be transferred (an integer value in case
        of the token's smallest subunit, a decimal value in case of the
        token's main unit).
    service_node_bid : tuple of ServiceNodeBid and int or None
        A pair of the address of the chosen service node and the
        service node's chosen bid. If none is specified,
        the registered service node bid with the lowest
        fee for the token transfer is automatically chosen.
    mainnet : bool, optional
        If True, the function is executed on mainnet. Otherwise, it is
        executed on testnet (default: testnet).

    Returns
    -------
    ServiceNodeTaskInfo
        Service node-related information of a token transfer.

    Raises
    ------
    PantosClientError
        If the token transfer cannot be executed.

    """
    _initialize_library(mainnet)
    request = _TransferInteractor.TransferTokensRequest(
        source_blockchain, destination_blockchain, sender_private_key,
        recipient_address, source_token_id, token_amount, service_node_bid)
    return _TransferInteractor().transfer_tokens(request)


def get_token_transfer_status(source_blockchain: Blockchain,
                              service_node_address: BlockchainAddress,
                              service_node_task_id: _uuid.UUID,
                              blocks_to_search: int | None = None, *,
                              mainnet: bool = False) -> TokenTransferStatus:
    """Get the status of a token transfer process.

    Parameters
    ----------
    source_blockchain : Blockchain
        The source blockchain of the token transfer.
    service_node_address : BlockchainAddress
        The address of the service node that is handling the token
        transfer.
    service_node_task_id : uuid.UUID
        The service node task ID of the token transfer.
    blocks_to_search : int or None
        The number of blocks to search for the destination transfer.
        If None, the search is performed until the genesis block.
    mainnet : bool, optional
        If True, the function is executed on mainnet. Otherwise, it is
        executed on testnet (default: testnet).

    Returns
    -------
    TokenTransferStatus
        The status of the token transfer transfer.

    Raises
    ------
    PantosClientError
        If the destination transfer cannot be found.

    """
    _initialize_library(mainnet)
    request = _TransferInteractor.TokenTransferStatusRequest(
        source_blockchain, service_node_address, service_node_task_id,
        blocks_to_search)
    return _TransferInteractor().get_token_transfer_status(request)


def deploy_pantos_compatible_token(token_name: str, token_symbol: str,
                                   token_decimals: int, token_pausable: bool,
                                   token_burnable: bool, token_supply: int,
                                   deployment_blockchains: list[Blockchain],
                                   payment_blockchain: Blockchain,
                                   payer_private_key: PrivateKey, *,
                                   mainnet: bool = False) -> _uuid.UUID:
    """Deploy a Pantos-compatible token on the given blockchains.

    Parameters
    ----------
    token_name : str
        The name of the token.
    token_symbol : str
        The symbol of the token.
    token_decimals : int
        The token's number of decimals.
    token_pausable : bool
        If the token is pausable.
    token_burnable : bool
        If the token is burnable.
    token_supply : int
        The supply of the token.
    deployment_blockchains : list of Blockchain
        The blockchains where the deployment will be requested.
    payment_blockchain : Blockchain
        The blockchain on which the payment for the fee will be made.
    payer_private_key : PrivateKey
        The unencrypted private key of the payer's account on the
        payment_blockchain.
    mainnet : bool, optional
        If True, the function is executed on mainnet. Otherwise, it is
        executed on testnet (default: testnet).

    Returns
    -------
    uuid.UUID
        The task ID of the token creator for the deployment process.

    Raises
    ------
    PantosClientError
        If the deployment process cannot be executed.

    """
    _initialize_library(mainnet)
    request = _TokenDeploymentInteractor.TokenDeploymentRequest(
        token_name, token_symbol, token_decimals, token_pausable,
        token_burnable, token_supply, deployment_blockchains,
        payment_blockchain, payer_private_key)
    return _TokenDeploymentInteractor().deploy_token(request)
