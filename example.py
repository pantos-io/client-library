#! /usr/bin/env python
"""Example usage of the Pantos client library.

"""
import pantos.client as pc

# Example retrieval of token balance
try:
    token_balance = pc.retrieve_token_balance(
        pc.Blockchain.ETHEREUM,
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

# More examples on example 2.py
