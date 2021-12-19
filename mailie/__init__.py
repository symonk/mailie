import importlib
import logging

from ._attachments import AttachmentStrategy
from ._attachments import FileAttachment
from ._dispatching import ASyncSMTPClient
from ._dispatching import SMTPClient
from ._email import Email
from ._header import EmailHeader
from ._policy import POLICIES
from ._senders import MailSender

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


version = importlib.metadata.version("mailie")  # type: ignore [attr-defined]


__all__ = [
    "Email",
    "POLICIES",
    "version",
    "EmailHeader",
    "SMTPClient",
    "ASyncSMTPClient",
    "FileAttachment",
    "AttachmentStrategy",
    "MailSender",
]
