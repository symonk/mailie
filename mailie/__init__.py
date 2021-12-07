import importlib

from ._email import EmailHeader
from ._email import email_factory
from ._policy import Policies
from ._senders import SimpleDispatcher

version = importlib.metadata.version("mailie")  # type: ignore [attr-defined]

__all__ = ["email_factory", "Policies", "version", "EmailHeader", "SimpleDispatcher"]
