"""Common exceptions for the Pantos client.

"""
from pantos.common.exceptions import BaseError


class ClientError(BaseError):
    """Base exception class for all Pantos client errors.

    """
    pass


class ClientLibraryError(ClientError):
    """Base exception class for all Pantos client library errors.

    """
    pass
