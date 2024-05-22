from __future__ import annotations

import dataclasses
import math
import time
import typing
import uuid

import requests
from pantos.common.blockchains.base import Blockchain
from pantos.common.entities import ServiceNodeBid
from pantos.common.entities import \
    TokenDeploymentRequest as TokenDeploymentSubmissionRequest
from pantos.common.types import BlockchainAddress
from pantos.common.types import PrivateKey

from pantos.client.library.blockchains import BlockchainClient
from pantos.client.library.blockchains import get_blockchain_client
from pantos.client.library.business.base import Interactor
from pantos.client.library.business.base import InteractorError
from pantos.client.library.configuration import config
from pantos.client.library.configuration import get_blockchain_config

_DEPLOYMENT_RESOURCE = 'deployment'

_PAYMENT_RESOURCE = 'payment'

_CHEAPEST_BID_RESOURCE = 'bids/cheapest'

_DEFAULT_VALID_UNTIL_BUFFER = 10000000


class TokenDeploymentInteractorError(InteractorError):
    """Exception class for all deployment interactor errors.

    """
    pass


class TokenDeploymentInteractor(Interactor):
    """Interactor for handling Pantos compatible token deployments.

    """
    @dataclasses.dataclass
    class TokenDeploymentRequest:
        """Request data for a new token deployment.

        Attributes
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
        valid_until_buffer : int
            The buffer in seconds added to the current timestamp plus
            the chosen service node bid's execution time.

        """
        token_name: str
        token_symbol: str
        token_decimals: int
        token_pausable: bool
        token_burnable: bool
        token_supply: int
        deployment_blockchains: typing.List[Blockchain]
        payment_blockchain: Blockchain
        payer_private_key: PrivateKey
        valid_until_buffer: int = _DEFAULT_VALID_UNTIL_BUFFER

    @dataclasses.dataclass
    class __DeploymentFee:
        """Deployment fee data for deploying Pantos compatible
        token smart contracts.

        Attributes
        ----------
        amount : int
            The amount to be paid.
        symbol : str
            The token symbol.

        """
        amount: int
        symbol: str

    @dataclasses.dataclass
    class __PaymentResponse:
        """Response data when requesting the payment from the
        Pantos token creator service.

        Attributes
        ----------
        receiver_address : str
            The receiver_address.
        deployment_fee_valid_until : int
            The timestamp until when the payment can be submitted
            to the token creator service (in seconds since the epoch).
        signature : str
            The signature that ensures the authenticity and valability
            of the payment response.
        deployment_fee : TokenDeploymentInteractor.__DeploymentFee
            The deployment fee object.

        """
        receiver_address: str
        deployment_fee_valid_until: int
        signature: str
        deployment_fee: TokenDeploymentInteractor.__DeploymentFee

    def deploy_token(self, request: TokenDeploymentRequest) -> uuid.UUID:
        """Deploy a Pantos compatible token.

        Parameters
        ----------
        request : TokenDeploymentRequest
            The request data for a new token deployment.

        Returns
        -------
        uuid.UUID
            The Pantos token creator's task ID.

        Raises
        ------
        TokenDeploymentInteractorError
            If the token deployment cannot be executed.

        """
        deployment_blockchain_ids = [
            blockchain.value for blockchain in request.deployment_blockchains
        ]
        service_node_address, service_node_bid = \
            self.__get_cheapest_bid_response(request.payment_blockchain)
        valid_until = self.__compute_valid_until(
            service_node_bid.execution_time, request.valid_until_buffer)
        blockchain_config = get_blockchain_config(request.payment_blockchain)
        pan_token_address = blockchain_config['tokens']['pan']
        source_blockchain_client = get_blockchain_client(
            request.payment_blockchain)
        payment_response = self.__get_payment_response(
            request.payment_blockchain, request.deployment_blockchains)
        recipient_address = BlockchainAddress(
            payment_response.receiver_address)
        transfer_signature_request = \
            BlockchainClient.ComputeTransferSignatureRequest(
                request.payer_private_key, recipient_address,
                pan_token_address,
                payment_response.deployment_fee.amount,
                service_node_address, service_node_bid, valid_until)
        transfer_signature_response = \
            source_blockchain_client.compute_transfer_signature(
                    transfer_signature_request)
        deployment_request = TokenDeploymentSubmissionRequest(
            deployment_blockchain_ids, request.token_name,
            request.token_symbol, request.token_decimals,
            request.token_pausable, request.token_burnable,
            request.token_supply, request.payment_blockchain.value,
            transfer_signature_response.sender_address,
            payment_response.deployment_fee.amount, payment_response.signature,
            payment_response.deployment_fee_valid_until, service_node_bid.fee,
            service_node_bid.execution_time, service_node_bid.valid_until,
            service_node_bid.signature,
            transfer_signature_response.sender_nonce, valid_until,
            transfer_signature_response.signature)
        return self.__submit_deployment_request(deployment_request)

    def __submit_deployment_request(
            self, request: TokenDeploymentSubmissionRequest) -> uuid.UUID:
        """Submit a deployment request to the Pantos token creator service.

        Parameters
        ----------
        request : TokenDeploymentSubmissionRequest
            Request data for submitting a new deployment request to the
            Pantos token creator service.

        Returns
        -------
        uuid.UUID
            The Pantos token creator's task ID.

        Raises
        ------
        TokenDeploymentInteractorError
            If the token deployment request cannot be submitted
            successfully.

        """
        payload = {
            'deployment_blockchain_ids': request.deployment_blockchain_ids,
            'token_name': request.token_name,
            'token_symbol': request.token_symbol,
            'token_decimals': request.token_decimals,
            'token_pausable': request.token_pausable,
            'token_burnable': request.token_burnable,
            'token_supply': request.token_supply,
            'payment_blockchain_id': request.payment_blockchain_id,
            'payer_address': request.payer_address,
            'deployment_fee': request.deployment_fee,
            'deployment_fee_valid_until': request.deployment_fee_valid_until,
            'deployment_fee_signature': request.deployment_fee_signature,
            'bid': {
                'fee': request.bid_fee,
                'execution_time': request.bid_execution_time,
                'valid_until': request.bid_valid_until,
                'signature': request.bid_signature
            },
            'payment_nonce': request.payment_nonce,
            'payment_valid_until': request.payment_valid_until,
            'payment_signature': request.payment_signature
        }
        token_creator_url_deployment = self.__build_resource_url(
            config['token_creator']['url'], _DEPLOYMENT_RESOURCE)
        try:
            token_creator_response = requests.post(
                token_creator_url_deployment, json=payload)
            token_creator_response.raise_for_status()
            task_id = token_creator_response.json()['task_id']
            return uuid.UUID(task_id)
        except (requests.exceptions.HTTPError, KeyError):
            raise TokenDeploymentInteractorError(
                'unable to submit a new deployment request', extra=request)

    def __get_payment_response(
            self, payment_blockchain: Blockchain,
            deployment_blockchains: typing.List[Blockchain]) \
            -> __PaymentResponse:
        """Get the payment response from the Pantos token
        creator service.

        Parameters
        ----------
        payment_blockchain : int
            The blockchain where the payment will be done.
        deployment_blockchains : list of Blockchain
            The list of deployment blockchains.

        Returns
        -------
        __PaymentResponse
            Response data when requesting the payment from the
            Pantos token creator service.

        Raises
        ------
        TokenDeploymentInteractorError
            If the token deployment request cannot be submitted
            successfully.

        """
        payment_blockchain_id = payment_blockchain.value
        deployment_blockchain_ids = [
            blockchain.value for blockchain in deployment_blockchains
        ]
        token_creator_url_deployment_fee = self.__build_resource_url(
            config['token_creator']['url'], _PAYMENT_RESOURCE)
        request = {
            'payment_blockchain_id': payment_blockchain_id,
            'deployment_blockchain_ids': deployment_blockchain_ids
        }
        try:
            token_creator_response = requests.post(
                token_creator_url_deployment_fee, json=request)
            token_creator_response.raise_for_status()
            json_response = token_creator_response.json()
            deployment_fee = json_response['fee']
            return self.__PaymentResponse(
                json_response['receiver_address'],
                json_response['valid_until'], json_response['signature'],
                self.__DeploymentFee(int(deployment_fee['amount']),
                                     deployment_fee['symbol']))
        except (requests.exceptions.HTTPError, KeyError):
            raise TokenDeploymentInteractorError(
                'unable to submit a new deployment request', extra=request)

    def __get_cheapest_bid_response(
            self, payment_blockchain: Blockchain) \
            -> typing.Tuple[BlockchainAddress, ServiceNodeBid]:
        """Get the cheapest bid response from the Pantos token
        creator service.

        Parameters
        ----------
        payment_blockchain : int
            The blockchain where the payment will be done.

        Returns
        -------
        Tuple[BlockchainAddress, ServiceNodeBid]
            A tuple containing the blockchain address of the service node with
            it's cheapest bid.

        Raises
        ------
        TokenDeploymentInteractorError
            If unable to get the cheapest bid response.

        """
        payment_blockchain_id = payment_blockchain.value
        token_creator_cheapest_bid_url = self.__build_resource_url(
            config['token_creator']['url'], _CHEAPEST_BID_RESOURCE)
        query_parameters = f'payment_blockchain_id={payment_blockchain_id}'
        try:
            token_creator_response = requests.get(
                f'{token_creator_cheapest_bid_url}?{query_parameters}')
            token_creator_response.raise_for_status()
            json_response = token_creator_response.json()
            service_node_bid = ServiceNodeBid(
                source_blockchain=payment_blockchain,
                destination_blockchain=payment_blockchain,
                fee=json_response['fee'],
                execution_time=json_response['execution_time'],
                valid_until=json_response['valid_until'],
                signature=json_response['signature'])
            return json_response['service_node_address'], service_node_bid
        except (requests.exceptions.HTTPError, KeyError):
            raise TokenDeploymentInteractorError(
                'unable to submit a cheapets bid request')

    def __compute_valid_until(self, execution_time: int,
                              valid_until_buffer: int) -> int:
        """Compute the valid until buffer for the payment.

        Parameters
        ----------
        execution_time : int
            The execution time of the payment.
        valid_until_buffer : int
            The buffer for sending the payment.

        Returns
        -------
        int
            The timestamp until when the payment can be submitted
            to the service node (in seconds since the epoch).

        """
        if valid_until_buffer < 0:
            raise TokenDeploymentInteractorError(
                '"valid until" buffer must be non-negative',
                valid_until_buffer=valid_until_buffer)
        return (math.ceil(time.time()) + execution_time + valid_until_buffer)

    def __build_resource_url(self, token_creator_url: str,
                             resource: str) -> str:
        """Build the token creator resource url.

        Parameters
        ----------
        token_creator_url : str
            The token creator url.

        Returns
        -------
        str
            The token creator resource url.

        """
        transfer_url = token_creator_url
        if not token_creator_url.endswith('/'):
            transfer_url += '/'
        transfer_url += resource
        return transfer_url
