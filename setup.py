import os

import setuptools

setuptools.setup(
    name='pantos-client-library',
    version=os.getenv('PANTOS_CLIENT_LIBRARY_VERSION'),
    description='Client library for the Pantos multi-blockchain system',
    packages=setuptools.find_packages(), package_data={
        'pantos': ['pantos-client-library.conf'],
        'pantos.common.blockchains.contracts': ['*.abi'],
        'pantos.client.library.blockchains.contracts': ['*.abi']
    }, install_requires=[
        'Cerberus==1.3.4', 'PyYAML==6.0', 'requests==2.31.0', 'web3==6.5.0'
    ])
