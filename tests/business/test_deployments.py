import unittest.mock

import pytest
import requests.exceptions

from pantos.client.library.business.deployments import \
    TokenDeploymentInteractor
from pantos.client.library.business.deployments import \
    TokenDeploymentInteractorError
from pantos.common.blockchains.base import Blockchain
from pantos.common.types import PrivateKey


@unittest.mock.patch('pantos.client.library.business.deployments.uuid.UUID')
@unittest.mock.patch('pantos.client.library.business.deployments.requests')
@unittest.mock.patch(
    'pantos.client.library.business.deployments.get_blockchain_client')
@unittest.mock.patch('pantos.client.library.business.deployments.config')
@unittest.mock.patch(
    'pantos.client.library.business.deployments.get_blockchain_config')
def test_deploy_token_correct(mocked_blockchain_config, mocked_config,
                              mocked_blockchain_client, mocked_request,
                              mocked_uuid):
    request = TokenDeploymentInteractor.TokenDeploymentRequest(
        'name', 'SYM', 10, True, False, 123, [Blockchain.ETHEREUM],
        Blockchain.ETHEREUM, PrivateKey('priv_key'))
    mocked_config.__getitem__().__getitem__.return_value = 'some_url'

    TokenDeploymentInteractor().deploy_token(request)

    mocked_blockchain_client.assert_called_once_with(Blockchain.ETHEREUM)
    mocked_blockchain_client().compute_transfer_signature.assert_called_once()


@unittest.mock.patch('pantos.client.library.business.deployments.requests.get',
                     side_effect=requests.exceptions.HTTPError(''))
@unittest.mock.patch(
    'pantos.client.library.business.deployments.get_blockchain_client')
@unittest.mock.patch('pantos.client.library.business.deployments.config')
@unittest.mock.patch(
    'pantos.client.library.business.deployments.get_blockchain_config')
def test_deploy_token_request_exception(mocked_blockchain_config,
                                        mocked_config,
                                        mocked_blockchain_client,
                                        mocked_post_request):
    request = TokenDeploymentInteractor.TokenDeploymentRequest(
        'name', 'SYM', 10, True, False, 123, [Blockchain.ETHEREUM],
        Blockchain.ETHEREUM, PrivateKey('priv_key'))
    mocked_bid = unittest.mock.Mock()
    mocked_bid.service_node_bid.execution_time = 600
    mocked_bid.service_node_address = 'some_addr'

    with pytest.raises(TokenDeploymentInteractorError):
        TokenDeploymentInteractor().deploy_token(request)


@unittest.mock.patch('pantos.client.library.business.deployments.requests')
@unittest.mock.patch('pantos.client.library.business.deployments.config')
def test_deploy_token_valid_until_error(mocked_config, mocked_request):
    mocked_config.__getitem__().__getitem__.return_value = 'some_url'
    request = TokenDeploymentInteractor.TokenDeploymentRequest(
        'name', 'SYM', 10, True, False, 123, [Blockchain.ETHEREUM],
        Blockchain.ETHEREUM, PrivateKey('priv_key'), -1)

    with pytest.raises(TokenDeploymentInteractorError):
        TokenDeploymentInteractor().deploy_token(request)


@unittest.mock.patch('pantos.client.library.business.deployments.uuid.UUID',
                     side_effect=requests.exceptions.HTTPError(''))
@unittest.mock.patch('pantos.client.library.business.deployments.requests.get')
@unittest.mock.patch('pantos.client.library.business.deployments.requests.post'
                     )
@unittest.mock.patch(
    'pantos.client.library.business.deployments.get_blockchain_client')
@unittest.mock.patch('pantos.client.library.business.deployments.config')
@unittest.mock.patch(
    'pantos.client.library.business.deployments.get_blockchain_config')
def test_deploy_token_unable_to_submit(mocked_blockchain_config, mocked_config,
                                       mocked_blockchain_client,
                                       mocked_request_post, mocked_request_get,
                                       mocked_uuid):
    request = TokenDeploymentInteractor.TokenDeploymentRequest(
        'name', 'SYM', 10, True, False, 123, [Blockchain.ETHEREUM],
        Blockchain.ETHEREUM, PrivateKey('priv_key'))
    mocked_bid = unittest.mock.Mock()
    mocked_bid.service_node_bid.execution_time = 600
    mocked_bid.service_node_address = 'some_addr'
    mocked_config.__getitem__().__getitem__.return_value = 'some_url'

    with pytest.raises(TokenDeploymentInteractorError):
        TokenDeploymentInteractor().deploy_token(request)
