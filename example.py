#! /usr/bin/env python
"""Example usage of the Pantos client library.

"""
import decimal
import getpass
import pathlib

import pantos.client as pc

# Example retrieval of token balance
try:
    token_balance = pc.retrieve_token_balance(
        pc.Blockchain.POLYGON,
        pc.BlockchainAddress('0xaAE34Ec313A97265635B8496468928549cdd4AB7'),
        pc.TokenSymbol('pan'))
    print('Token balance: {}'.format(token_balance))
except pc.PantosClientError:
    # Handle exception
    raise

# Example retrieval of service node bids
try:
    service_node_bids = pc.retrieve_service_node_bids(pc.Blockchain.AVALANCHE,
                                                      pc.Blockchain.CRONOS)
    print('Service node bids: {}'.format(service_node_bids))
except pc.PantosClientError:
    # Handle exception
    raise

# Example token transfer
password = getpass.getpass('Keystore password: ')
try:
    private_key = pc.load_private_key(pc.Blockchain.ETHEREUM,
                                      pathlib.Path('my_client.keystore'),
                                      password)
    task_id = pc.transfer_tokens(
        pc.Blockchain.ETHEREUM, pc.Blockchain.BNB_CHAIN, private_key,
        pc.BlockchainAddress('0xaAE34Ec313A97265635B8496468928549cdd4AB7'),
        pc.TokenSymbol('pan'), decimal.Decimal('3.1'))
    print('Task ID of service node: {}'.format(task_id))
except pc.PantosClientError:
    # Handle exception
    raise

# Example of deploying a token contract
password = getpass.getpass('Keystore password: ')
try:
    private_key = pc.load_private_key(pc.Blockchain.ETHEREUM,
                                      pathlib.Path('my_client.keystore'),
                                      password)
    deployment_blockchains = [pc.Blockchain.ETHEREUM]
    payment_blockchain = pc.Blockchain.ETHEREUM
    task_id = pc.deploy_pantos_compatible_token('Test_cli', 'TCLI', 7, True,
                                                False, 54321,
                                                deployment_blockchains,
                                                payment_blockchain,
                                                private_key)
    print('Task ID deployment: {}'.format(task_id))
except pc.PantosClientError:
    # Handle exception
    raise
