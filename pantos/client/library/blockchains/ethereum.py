"""Module for Ethereum-specific clients and errors.

"""
import secrets
import typing

import eth_account.messages
import hexbytes
import web3
import web3.contract
from pantos.common.blockchains.base import Blockchain
from pantos.common.blockchains.base import NodeConnections
from pantos.common.blockchains.enums import ContractAbi
from pantos.common.blockchains.ethereum import EthereumUtilities
from pantos.common.types import BlockchainAddress
from pantos.common.types import PrivateKey

from pantos.client.library.blockchains.base import BlockchainClient
from pantos.client.library.blockchains.base import BlockchainClientError
from pantos.client.library.constants import TOKEN_SYMBOL_PAN

Web3Contract: typing.TypeAlias = NodeConnections.Wrapper[
    web3.contract.Contract]


class EthereumClientError(BlockchainClientError):
    """Exception class for all Ethereum client errors.

    """
    pass


class EthereumClient(BlockchainClient):
    """Ethereum-specific blockchain client.

    """

    def compute_transfer_signature(
            self, request: BlockchainClient.ComputeTransferSignatureRequest) \
            -> BlockchainClient.ComputeTransferSignatureResponse:
        # Docstring inherited
        try:
            blockchain_id = self.get_blockchain().value
            sender_address = self._account_id_to_account_address(
                request.sender_private_key)
            hub_address = self._get_config()['hub']
            forwarder_address = self._get_config()['forwarder']
            pan_token_address = self._get_config()['tokens'][TOKEN_SYMBOL_PAN]
            node_connections = self._get_utilities().create_node_connections()
            hub_contract = self._create_hub_contract(node_connections)
            sender_nonce = self.__generate_sender_nonce(
                hub_contract, sender_address)
            base_message = web3.Web3.solidity_keccak([
                'uint256', 'address', 'address', 'address', 'uint256',
                'address', 'uint256', 'uint256', 'uint256', 'address',
                'address', 'address'
            ], [
                blockchain_id, sender_address, request.recipient_address,
                request.token_address, request.token_amount,
                request.service_node_address, request.service_node_bid.fee,
                sender_nonce, request.valid_until, hub_address,
                forwarder_address, pan_token_address
            ])
            signature = self.__sign_message(request.sender_private_key,
                                            base_message)
            return BlockchainClient.ComputeTransferSignatureResponse(
                sender_address, sender_nonce, signature)
        except Exception:
            raise self._create_error(
                'unable to compute a single-chain transfer signature',
                request=request)

    def compute_transfer_from_signature(
            self,
            request: BlockchainClient.ComputeTransferFromSignatureRequest) \
            -> BlockchainClient.ComputeTransferFromSignatureResponse:
        # Docstring inherited
        try:
            source_blockchain_id = self.get_blockchain().value
            destination_blockchain_id = request.destination_blockchain.value
            sender_address = self._account_id_to_account_address(
                request.sender_private_key)
            hub_address = self._get_config()['hub']
            forwarder_address = self._get_config()['forwarder']
            pan_token_address = self._get_config()['tokens'][TOKEN_SYMBOL_PAN]
            node_connections = self._get_utilities().create_node_connections()
            hub_contract = self._create_hub_contract(node_connections)
            sender_nonce = self.__generate_sender_nonce(
                hub_contract, sender_address)
            base_message = web3.Web3.solidity_keccak([
                'uint256', 'uint256', 'address', 'string', 'address', 'string',
                'uint256', 'address', 'uint256', 'uint256', 'uint256',
                'address', 'address', 'address'
            ], [
                source_blockchain_id, destination_blockchain_id,
                sender_address, request.recipient_address,
                request.source_token_address,
                request.destination_token_address, request.token_amount,
                request.service_node_address, request.service_node_bid.fee,
                sender_nonce, request.valid_until, hub_address,
                forwarder_address, pan_token_address
            ])
            signature = self.__sign_message(request.sender_private_key,
                                            base_message)
            return BlockchainClient.ComputeTransferFromSignatureResponse(
                sender_address, sender_nonce, signature)
        except Exception:
            raise self._create_error(
                'unable to compute a cross-chain transfer signature',
                request=request)

    def is_valid_recipient_address(self, recipient_address: str) -> bool:
        # Docstring inherited
        is_valid_address = int(recipient_address, 0) != 0 and \
            web3.Web3.is_checksum_address(recipient_address)
        return is_valid_address

    @classmethod
    def get_blockchain(cls) -> Blockchain:
        # Docstring inherited
        return Blockchain.ETHEREUM

    @classmethod
    def get_error_class(cls) -> type[BlockchainClientError]:
        # Docstring inherited
        return EthereumClientError

    def read_external_token_address(
            self, token_address: BlockchainAddress,
            destination_blockchain: Blockchain) -> BlockchainAddress:
        # Docstring inherited
        try:
            node_connections = self._get_utilities().create_node_connections()
            hub_contract = self._create_hub_contract(node_connections)
            external_token_record = \
                hub_contract.caller().getExternalTokenRecord(
                    token_address, destination_blockchain.value).get()
            assert len(external_token_record) == 2
            external_token_active = external_token_record[0]
            if not external_token_active:
                raise self._create_error(
                    'external token is not active',
                    token_address=token_address,
                    destination_blockchain=destination_blockchain)
            external_token_address = external_token_record[1]
            assert isinstance(external_token_address, str)
            return BlockchainAddress(external_token_address)
        except EthereumClientError:
            raise
        except Exception:
            raise self._create_error(
                'unable to read an external token address',
                token_address=token_address,
                destination_blockchain=destination_blockchain)

    def read_service_node_addresses(self) -> typing.List[BlockchainAddress]:
        # Docstring inherited
        try:
            node_connections = self._get_utilities().create_node_connections()
            hub_contract = self._create_hub_contract(node_connections)
            service_node_addresses = hub_contract.caller().getServiceNodes(
            ).get()
            return [
                BlockchainAddress(service_node_address)
                for service_node_address in sorted(service_node_addresses)
            ]
        except Exception:
            raise self._create_error(
                'unable to read the active service node addresses')

    def read_service_node_url(self,
                              service_node_address: BlockchainAddress) -> str:
        # Docstring inherited
        try:
            node_connections = self._get_utilities().create_node_connections()
            hub_contract = self._create_hub_contract(node_connections)
            service_node_record = hub_contract.caller().getServiceNodeRecord(
                service_node_address).get()
            assert len(service_node_record) == 6
            service_node_active = service_node_record[0]
            if not service_node_active:
                raise self._create_error(
                    'service node is not active',
                    service_node_address=service_node_address)
            service_node_url = service_node_record[1]
            assert isinstance(service_node_url, str)
            return service_node_url
        except EthereumClientError:
            raise
        except Exception:
            raise self._create_error('unable to read a service node URL',
                                     service_node_address=service_node_address)

    def read_token_decimals(self, token_address: BlockchainAddress) -> int:
        # Docstring inherited
        try:
            node_connections = self._get_utilities().create_node_connections()
            token_contract = self._create_token_contract(
                node_connections, token_address)
            return token_contract.caller().decimals().get()
        except Exception:
            raise self._create_error(
                'unable to read the number of decimals of a token',
                token_address=token_address)

    def _create_hub_contract(
            self, node_connections: NodeConnections) \
            -> NodeConnections.Wrapper[web3.contract.Contract]:
        try:
            return self._get_utilities().create_contract(
                self._get_config()['hub'], ContractAbi.PANTOS_HUB,
                node_connections)
        except Exception:
            raise self._create_error(
                'unable to create a hub contract instance')

    def _create_token_contract(
            self, node_connections: NodeConnections,
            token_address: BlockchainAddress) -> Web3Contract:
        try:
            return self._get_utilities().create_contract(
                token_address, ContractAbi.PANTOS_TOKEN, node_connections)
        except Exception:
            raise self._create_error(
                'unable to create a token contract instance')

    def _get_utilities(self) -> EthereumUtilities:
        # Docstring inherited
        return typing.cast(EthereumUtilities, super()._get_utilities())

    def __generate_sender_nonce(self, hub_contract: Web3Contract,
                                sender_address: BlockchainAddress) -> int:
        while True:
            sender_nonce = secrets.randbits(256)
            if hub_contract.caller().isValidSenderNonce(
                    sender_address, sender_nonce).get():
                return sender_nonce

    def __sign_message(self, private_key: PrivateKey,
                       base_message: hexbytes.HexBytes) -> str:
        message = eth_account.messages.encode_defunct(base_message)
        signed_message = web3.Account.sign_message(message,
                                                   private_key=private_key)
        return signed_message.signature.hex()
