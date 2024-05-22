"""Top-level package of the Pantos client library.

"""
import ctypes as _ctypes
import multiprocessing as _multiprocessing

from pantos.common.configuration import ConfigError as _ConfigError

from pantos.client.library.configuration import load_config as _load_config
from pantos.client.library.exceptions import \
    ClientLibraryError as _ClientLibraryError

_initialized = _multiprocessing.Value(_ctypes.c_bool, False)


def initialize_library() -> None:
    """Initialize the Pantos client library. The function is thread-safe
    and performs the initialization only once at the first invocation.

    Raises
    ------
    ClientLibraryError
        If the library cannot be initialized.

    """
    with _initialized.get_lock():
        if not _initialized.value:  # type: ignore
            try:
                _load_config()
            except _ConfigError:
                raise _ClientLibraryError("error loading config")
            _initialized.value = True  # type: ignore
    # _multiprocessing.Value type bug:
    # https://github.com/python/mypy/issues/12299
