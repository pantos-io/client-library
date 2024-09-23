import unittest.mock

import pytest
import semantic_version  # type: ignore
from pantos.common.configuration import ConfigError

from pantos.client.library import _initialized
from pantos.client.library import initialize_library
from pantos.client.library.exceptions import ClientLibraryError
from pantos.client.library.protocol import is_supported_protocol_version


@pytest.mark.parametrize('mainnet', [False, True])
@pytest.mark.parametrize('initialized', [False, True])
@unittest.mock.patch('pantos.client.library._config')
@unittest.mock.patch('pantos.client.library._load_config')
def test_initialize_library_correct(mock_load_config, mock_config, initialized,
                                    mainnet, protocol_version):
    _initialized.value = initialized
    mock_config.__getitem__.side_effect = _get_config(
        protocol_version).__getitem__

    initialize_library(mainnet)

    assert _initialized.value
    if initialized:
        mock_load_config.assert_not_called()
    else:
        mock_load_config.assert_called_once()


@pytest.mark.parametrize('mainnet', [False, True])
@unittest.mock.patch('pantos.client.library._load_config')
def test_initialize_library_config_load_error(mock_load_config, mainnet):
    _initialized.value = False
    mock_load_config.side_effect = ConfigError('')

    with pytest.raises(ClientLibraryError) as exception_info:
        initialize_library(mainnet)

    raised_error = exception_info.value
    assert isinstance(raised_error.__context__, ConfigError)


@pytest.mark.parametrize('mainnet', [False, True])
@unittest.mock.patch('pantos.client.library._config')
@unittest.mock.patch('pantos.client.library._load_config')
def test_initialize_library_unsupported_protocol_version(
        mock_load_config, mock_config, mainnet):
    _initialized.value = False
    protocol_version = semantic_version.Version('123.456.789')
    assert not is_supported_protocol_version(protocol_version)
    mock_config.__getitem__.side_effect = _get_config(
        protocol_version).__getitem__

    with pytest.raises(ClientLibraryError) as exception_info:
        initialize_library(mainnet)

    raised_error = exception_info.value
    assert raised_error.details['protocol_version'] == protocol_version
    assert raised_error.__context__ is None


def _get_config(protocol_version):
    return {
        'protocol': {
            'mainnet': str(protocol_version),
            'testnet': str(protocol_version)
        }
    }
