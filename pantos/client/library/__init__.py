"""Top-level package of the Pantos client library.

"""
import ctypes as _ctypes
import multiprocessing as _multiprocessing

import semantic_version as _semantic_version  # type: ignore
from pantos.common.configuration import ConfigError as _ConfigError

from pantos.client.library.configuration import config as _config
from pantos.client.library.configuration import load_config as _load_config
from pantos.client.library.exceptions import \
    ClientLibraryError as _ClientLibraryError
from pantos.client.library.protocol import \
    is_supported_protocol_version as _is_supported_protocol_version

_initialized = _multiprocessing.Value(_ctypes.c_bool, False)


def initialize_library(mainnet: bool) -> None:
    """Initialize the Pantos client library. The function is thread-safe
    and performs the initialization only once at the first invocation.

    Parameters
    ----------
    mainnet : bool
        If True, the client library is initialized for mainnet
        operation. Otherwise, it is initialized for testnet operation.

    Raises
    ------
    ClientLibraryError
        If the library cannot be initialized.

    """
    with _initialized.get_lock():
        if not _initialized.value:
            try:
                _load_config()
            except _ConfigError:
                raise _ClientLibraryError('error loading config')
            environment = 'mainnet' if mainnet else 'testnet'
            protocol_version = _semantic_version.Version(
                _config['protocol'][environment])
            if not _is_supported_protocol_version(protocol_version):
                raise _ClientLibraryError(
                    'unsupported Pantos protocol version',
                    protocol_version=protocol_version)
            _initialized.value = True
