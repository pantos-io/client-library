<img src="https://raw.githubusercontent.com/pantos-io/client-library/img/pantos-logo-full.svg" alt="Pantos logo" align="right" width="120" />

[![CI](https://github.com/pantos-io/client-library/actions/workflows/ci.yaml/badge.svg?branch=main)](https://github.com/pantos-io/client-library/actions/workflows/ci.yaml)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=pantos-io_client-library2&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=pantos-io_client-library2)


# Pantos Client Library

## 1. Introduction

### 1.1 Overview

Welcome to the documentation for Pantos Client Library, a powerful tool for engaging with the Pantos system. This documentation aims to provide developers with comprehensive information on how to use the features offered by the library.

### 1.2 Features

The Pantos Client Library API exposes the following functionalities:

1. Loading the private key from a keystore file
2. Retrieve the service node bids
3. Retrieve the balance of a token
4. Transfer tokens
5. Deploy PANDAS tokens

## 2. Installation

### 2.1 Prerequisites

Please make sure that your development environment meets the following requirements:

#### Keystore File (Wallet)

The library requires a private key encrypted with a password. 

Since, for the moment, the Pantos protocol supports only EVM blockchains, only an Ethereum account keystore file is sufficient. It can be created with tools such as https://vanity-eth.tk/.

One of the most significant advantages of using Pantos is that the protocol has been designed to require minimal user friction when cross-chain operations are performed. Therefore, when using the Pantos products, you must top up your wallet only with PAN tokens.

#### Python Version

The Pantos Client Library supports **Python 3.10** or higher. Ensure that you have the correct Python version installed before the installation steps. You can download the latest version of Python from the official [Python website](https://www.python.org/downloads/).



### 2.2 Pypi package

The Pantos Client Library is available as a package from [Pypi](https://pypi.org/project/pantos-client-library/).

```bash
$ virtualenv env
$ source env/bin/activate
$ pip install pantos-client-library
```

### 2.3 Source code

The Pantos Client Library has been tested with the library versions specified in **poetry.lock**.

#### Poetry

Poetry is our tool of choice for dependency management and packaging.

Installing: 
https://python-poetry.org/docs/#installing-with-the-official-installer
or
https://python-poetry.org/docs/#installing-with-pipx

You can use the following lines to install poetry using `virtualenv`.

```bash
$ virtualenv env
$ source env/bin/activate
$ pip install poetry
```

By default poetry creates the venv directory under under ```{cache-dir}/virtualenvs```. If you opt for creating the virtualenv inside the project’s root directory, execute the following command:

```bash
poetry config virtualenvs.in-project true
```

#### Clone the repository

Clone the repository to your local machine:

```bash
$ git clone https://github.com/pantos-io/client-library.git
$ cd client-library
```

#### Libraries

Install the project dependencies:

```bash
$ poetry install --no-root
```

## 3. Usage

### 3.1 Configuration

The configuration can be found in **client-library.yml**.

The library already has a set configuration for our testnet environment, but feel free to adapt it to your needs.

### 3.2 Examples

The **api.py** exposes the public functions of the library.

The following example leverages all the functionalities of the library:

```bash
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

# Read private key from file
if not pathlib.Path('my_client.keystore').exists():
    raise FileNotFoundError('Keystore file not found')
with open('my_client.keystore', 'r') as keystore_file:
    keystore = keystore_file.read()

# Example token transfer
password = getpass.getpass('Keystore password: ')
try:
    private_key = pc.decrypt_private_key(pc.Blockchain.ETHEREUM, keystore,
                                         password)
    token_transfer_response = pc.transfer_tokens(
        pc.Blockchain.ETHEREUM, pc.Blockchain.BNB_CHAIN, private_key,
        pc.BlockchainAddress('0xaAE34Ec313A97265635B8496468928549cdd4AB7'),
        pc.TokenSymbol('pan'), decimal.Decimal('3.1'))
    print(f'Token transfer response: {token_transfer_response}')
except pc.PantosClientError:
    # Handle exception
    raise

# Example of getting a token transfer status
try:
    token_transfer_status = pc.get_token_transfer_status(
        pc.Blockchain.ETHEREUM, token_transfer_response.service_node_address,
        token_transfer_response.task_id)
    print(f'Token transfer status: {token_transfer_status}')
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
```

## 4. Contributing

For contributions check our [code of conduct](CODE_OF_CONDUCT.md).
