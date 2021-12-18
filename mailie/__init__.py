import importlib
import logging

from ._dispatching import ASyncSMTPClient
from ._dispatching import SMTPClient
from ._email import Email
from ._header import EmailHeader
from ._policy import POLICIES

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


version = importlib.metadata.version("mailie")  # type: ignore [attr-defined]

__all__ = ["Email", "POLICIES", "version", "EmailHeader", "SMTPClient", "ASyncSMTPClient"]
