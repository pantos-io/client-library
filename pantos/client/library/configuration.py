"""Module for loading, validating, and accessing the client library's
configuration.

"""
import itertools
import typing

from pantos.common.blockchains.base import Blockchain
from pantos.common.configuration import Config

_DEFAULT_FILE_NAME: typing.Final[str] = 'client-library.yml'
"""Default configuration file name."""

config = Config(_DEFAULT_FILE_NAME)
"""Singleton object holding the configuration values."""

_VALIDATION_SCHEMA_BLOCKCHAIN = {
    'type': 'dict',
    'schema': {
        'active': {
            'type': 'boolean',
            'default': True
        },
        'provider': {
            'type': 'string',
            'required': True
        },
        'fallback_providers': {
            'type': 'list',
            'required': False,
            'schema': {
                'type': 'string',
            }
        },
        'average_block_time': {
            'type': 'integer',
            'required': True
        },
        'blocks_per_query': {
            'type': 'integer',
            'required': True,
            'min': 1
        },
        'chain_id': {
            'type': 'integer',
            'required': True
        },
        'confirmations': {
            'type': 'integer',
            'required': True
        },
        'hub': {
            'type': 'string',
            'required': True
        },
        'forwarder': {
            'type': 'string',
            'required': True
        },
        'tokens': {
            'type': 'dict',
            'required': True,
            'keysrules': {
                'type': 'string',
                'regex': '[a-z0-9]+'
            },
            'valuesrules': {
                'type': 'string'
            }
        }
    }
}
"""Schema for validating a blockchain entry in the configuration file."""

_VALIDATION_SCHEMA = {
    'protocol': {
        'type': 'dict',
        'required': True,
        'schema': {
            'mainnet': {
                'type': 'string',
                'required': True,
                'regex': r'^[0-9]+\.[0-9]+\.[0-9]+$'
            },
            'testnet': {
                'type': 'string',
                'required': True,
                'regex': r'^[0-9]+\.[0-9]+\.[0-9]+$'
            }
        }
    },
    'token_creator': {
        'type': 'dict',
        'schema': {
            'url': {
                'type': 'string',
                'required': True
            }
        }
    },
    'service_nodes': {
        'type': 'dict',
        'schema': {
            'timeout': {
                'type': 'float',
                'required': True
            }
        }
    },
    'blockchains': {
        'type': 'dict',
        'schema': dict(
            zip([b.name.lower() for b in Blockchain],
                itertools.repeat(_VALIDATION_SCHEMA_BLOCKCHAIN)))
    }
}
"""Schema for validating the configuration file."""


def get_blockchain_config(
        blockchain: Blockchain) -> typing.Dict[str, typing.Any]:
    """Get a blockchain-specific configuration dictionary.

    Parameters
    ----------
    blockchain : Blockchain
        The blockchain to get the configuration for.

    Returns
    -------
    dict
        The blockchain-specific configuration.

    """
    return config['blockchains'][blockchain.name.lower()]


def load_config(file_path: typing.Optional[str] = None,
                reload: bool = True) -> None:
    """Load the configuration from a configuration file.

    Parameters
    ----------
    file_path : str or None
        The path to the configuration file (typical configuration file
        locations are searched if none is specified).
    reload : bool
        If True, the configuration is also loaded if it was already
        loaded before.

    Raises
    ------
    pantos.common.configuration.ConfigError
        If the configuration cannot be loaded (e.g. due to an invalid
        configuration file).

    See Also
    --------
    Config.load

    """
    if reload or not config.is_loaded():
        config.load(_VALIDATION_SCHEMA, file_path)
