"""Business logic for handling Pantos-compatible tokens.

"""
import dataclasses
import decimal

from pantos.common.blockchains.base import Blockchain
from pantos.common.types import AccountId
from pantos.common.types import Amount
from pantos.common.types import BlockchainAddress
from pantos.common.types import TokenId
from pantos.common.types import TokenSymbol

from pantos.client.library.blockchains import get_blockchain_client
from pantos.client.library.business.base import Interactor
from pantos.client.library.business.base import InteractorError
from pantos.client.library.configuration import get_blockchain_config


class TokenInteractorError(InteractorError):
    """Exception class for all token interactor errors.

    """
    pass


class TokenInteractor(Interactor):
    """Interactor for handling Pantos-compatible tokens.

    """
    def convert_amount_to_main_unit(self, blockchain: Blockchain,
                                    token_id: TokenId,
                                    amount_subunit: int) -> decimal.Decimal:
        """Convert an amount from a token's smallest subunit to its main
        unit.

        Parameters
        ----------
        blockchain : Blockchain
            The blockchain to convert the token amount for.
        token_id : TokenId
            The identifier of the token.
        amount_subunit : int
            The amount in the token's smallest subunit.

        Returns
        -------
        decimal.Decimal
            The amount in the token's main unit.

        Raises
        ------
        TokenInteractorError
            If the amount cannot be converted.

        """
        try:
            if amount_subunit < 0:
                raise TokenInteractorError('amount must be non-negative',
                                           amount_subunit=amount_subunit)
            if amount_subunit == 0:
                return decimal.Decimal(0)
            token_address = self.__token_id_to_token_address(
                blockchain, token_id)
            blockchain_client = get_blockchain_client(blockchain)
            token_decimals = blockchain_client.read_token_decimals(
                token_address)
            assert token_decimals >= 0
            return decimal.Decimal(amount_subunit) / (10**token_decimals)
        except TokenInteractorError:
            raise
        except Exception:
            raise TokenInteractorError(
                'unable to convert an amount to a token\'s main unit',
                blockchain=blockchain, token_id=token_id,
                amount_subunit=amount_subunit)

    def convert_amount_to_subunit(self, blockchain: Blockchain,
                                  token_id: TokenId,
                                  amount_main_unit: decimal.Decimal) -> int:
        """Convert an amount from a token's main unit to its smallest
        subunit.

        Parameters
        ----------
        blockchain : Blockchain
            The blockchain to convert the token amount for.
        token_id : TokenId
            The identifier of the token.
        amount_main_unit : decimal.Decimal
            The amount in the token's main unit.

        Returns
        -------
        int
            The amount in the token's smallest subunit.

        Raises
        ------
        TokenInteractorError
            If the amount cannot be converted.

        """
        try:
            if amount_main_unit < 0:
                raise TokenInteractorError('amount must be non-negative',
                                           amount_main_unit=amount_main_unit)
            if amount_main_unit == 0:
                return 0
            token_address = self.__token_id_to_token_address(
                blockchain, token_id)
            blockchain_client = get_blockchain_client(blockchain)
            token_decimals = blockchain_client.read_token_decimals(
                token_address)
            assert token_decimals >= 0
            amount_subunit = amount_main_unit * (10**token_decimals)
            amount_subunit_integer = int(amount_subunit)
            if (amount_subunit - amount_subunit_integer) != 0:
                raise TokenInteractorError(
                    'amount must not have more decimals than token',
                    amount_main_unit=amount_main_unit,
                    token_decimals=token_decimals)
            return amount_subunit_integer
        except TokenInteractorError:
            raise
        except Exception:
            raise TokenInteractorError(
                'unable to convert an amount to a token\'s smallest subunit',
                blockchain=blockchain, token_id=token_id,
                amount_main_unit=amount_main_unit)

    def find_token_address(self, blockchain: Blockchain,
                           token_symbol: TokenSymbol) -> BlockchainAddress:
        """Find the blockchain address of a token by its symbol.

        Parameters
        ----------
        blockchain : Blockchain
            The blockchain to find the token address on.
        token_symbol : TokenSymbol
            The symbol of the token.

        Returns
        -------
        BlockchainAddress
            The found token address.

        Raises
        ------
        TokenInteractorError
            If the token symbol is unknown.

        """
        blockchain_config = get_blockchain_config(blockchain)
        token_address = blockchain_config['tokens'].get(token_symbol.lower())
        if token_address is None:
            raise TokenInteractorError('token symbol unknown',
                                       blockchain=blockchain,
                                       token_symbol=token_symbol)
        return BlockchainAddress(token_address)

    @dataclasses.dataclass
    class FindTokenAddressesResponse:
        """Response data for finding blockchain addresses of a token on
        a source and destination blockchain.

        Attributes
        ----------
        source_token_address : BlockchainAddress
            The token's address on the source blockchain.
        destination_token_address : BlockchainAddress
            The token's address on the destination blockchain.

        """
        source_token_address: BlockchainAddress
        destination_token_address: BlockchainAddress

    def find_token_addresses(
            self, source_blockchain: Blockchain,
            destination_blockchain: Blockchain,
            source_token_id: TokenId) -> FindTokenAddressesResponse:
        """Find the blockchain addresses of a token on a source and
        destination blockchain.

        Parameters
        ----------
        source_blockchain : Blockchain
            The source blockchain to find the token address on.
        destination_blockchain : Blockchain
            The destination blockchain to find the token address on.
        source_token_id : TokenId
            The identifier of the token on the source blockchain.

        Returns
        -------
        FindTokenAddressesResponse
            The response data containing the source and destination
            token addresses.

        Raises
        ------
        TokenInteractorError
            If the token identifier is unknown or the token addresses
            cannot be searched for.

        """
        try:
            source_token_address = self.__token_id_to_token_address(
                source_blockchain, source_token_id)
            if source_blockchain is destination_blockchain:
                destination_token_address = source_token_address
            elif isinstance(source_token_id, TokenSymbol):
                destination_token_address = self.find_token_address(
                    destination_blockchain, source_token_id)
            else:
                source_blockchain_client = get_blockchain_client(
                    source_blockchain)
                destination_token_address = \
                    source_blockchain_client.read_external_token_address(
                        source_token_address, destination_blockchain)
            return TokenInteractor.FindTokenAddressesResponse(
                source_token_address, destination_token_address)
        except TokenInteractorError:
            raise
        except Exception:
            raise TokenInteractorError(
                'unable to search for token addresses',
                source_blockchain=source_blockchain,
                destination_blockchain=destination_blockchain,
                source_token_id=source_token_id)

    @dataclasses.dataclass
    class RetrieveTokenBalanceRequest:
        """Request data for retrieving the token balance of a blockchain
        account.

        Attributes
        ----------
        blockchain : Blockchain
            The blockchain to retrieve the token balance on.
        token_id : TokenId
            The identifier of the token.
        account_id : AccountId
            The identifier of the blockchain account.
        return_in_main_unit : bool
            True if the token balance is to be returned in the token's
            main unit, False if it is to be returned in the token's
            smallest subunit.

        """
        blockchain: Blockchain
        token_id: TokenId
        account_id: AccountId
        return_in_main_unit: bool

    def retrieve_token_balance(self,
                               request: RetrieveTokenBalanceRequest) -> Amount:
        """Retrieve the token balance of a blockchain account.

        Parameters
        ----------
        request : RetrieveTokenBalanceRequest
            The request data for retrieving the token balance.

        Returns
        -------
        Amount
            The token balance of the blockchain account (an integer
            value in case of the token's smallest subunit, a decimal
            value in case of the token's main unit).

        Raises
        ------
        TokenInteractorError
            If the token balance cannot be retrieved.

        """
        try:
            token_address = self.__token_id_to_token_address(
                request.blockchain, request.token_id)
            blockchain_client = get_blockchain_client(request.blockchain)
            token_balance = blockchain_client.read_token_balance(
                token_address, request.account_id)
            assert token_balance >= 0
            return (token_balance if not request.return_in_main_unit
                    else self.convert_amount_to_main_unit(
                        request.blockchain, token_address, token_balance))
        except TokenInteractorError:
            raise
        except Exception:
            raise TokenInteractorError(
                'unable to retrieve the token balance of a blockchain account',
                request=request)

    def __token_id_to_token_address(self, blockchain: Blockchain,
                                    token_id: TokenId) -> BlockchainAddress:
        if isinstance(token_id, BlockchainAddress):
            return token_id
        return self.find_token_address(blockchain, token_id)
