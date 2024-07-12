import unittest.mock

from pantos.common.blockchains.base import Blockchain

from pantos.client.library.api import deploy_pantos_compatible_token
from pantos.client.library.api import get_token_transfer_status
from pantos.client.library.business.deployments import \
    TokenDeploymentInteractor
from pantos.client.library.business.transfers import TransferInteractor


@unittest.mock.patch('pantos.client.library.api._initialize_library')
@unittest.mock.patch.object(TokenDeploymentInteractor, 'deploy_token')
def test_deploy_pantos_compatible_token_correct(mocked_deploy_token,
                                                mocked_initialize_library):
    deployment_blockchains = [Blockchain.ETHEREUM]
    payment_blockchain = Blockchain.ETHEREUM
    deploy_pantos_compatible_token('Test_cli', 'TCLI', 7, True, False, 54321,
                                   deployment_blockchains, payment_blockchain,
                                   'priv_key')

    mocked_initialize_library.assert_called_once()
    mocked_deploy_token.assert_called_once()


@unittest.mock.patch.object(TransferInteractor, 'get_token_transfer_status')
@unittest.mock.patch('pantos.client.library.api._initialize_library')
def test_get_token_transfer_status_correct(mocked_initialize_library,
                                           mocked_get_token_transfer_status,
                                           service_node_1, task_uuid):
    get_token_transfer_status(Blockchain.ETHEREUM, service_node_1, task_uuid)

    mocked_initialize_library.assert_called_once()
    mocked_get_token_transfer_status.assert_called_once_with(
        TransferInteractor.TokenTransferStatusRequest(Blockchain.ETHEREUM,
                                                      service_node_1,
                                                      task_uuid))
