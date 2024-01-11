import unittest.mock

from pantos.client.library.api import deploy_pantos_compatible_token
from pantos.client.library.business.deployments import \
    TokenDeploymentInteractor as _TokenDeploymentInteractor
from pantos.common.blockchains.base import Blockchain


@unittest.mock.patch('pantos.client.library.api._initialize_library')
@unittest.mock.patch.object(_TokenDeploymentInteractor, 'deploy_token')
def test_deploy_pantos_compatible_token_correct(mocked_initialize_library,
                                                mocked_deploy_token):
    deployment_blockchains = [Blockchain.ETHEREUM]
    payment_blockchain = Blockchain.ETHEREUM
    deploy_pantos_compatible_token('Test_cli', 'TCLI', 7, True, False, 54321,
                                   deployment_blockchains, payment_blockchain,
                                   'priv_key')

    mocked_initialize_library.assert_called_once()
    mocked_deploy_token.assert_called_once()
