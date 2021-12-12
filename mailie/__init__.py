import importlib

from ._email import Email
from ._header import EmailHeader
from ._policy import Policies
from ._senders import SimpleDispatcher

version = importlib.metadata.version("mailie")  # type: ignore [attr-defined]

__all__ = ["Email", "Policies", "version", "EmailHeader", "SimpleDispatcher"]
