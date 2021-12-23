import importlib
import logging

from ._attachments import AttachmentStrategy
from ._attachments import FileAttachment
from ._attachments import HtmlContent
from ._dispatching import ASyncSMTPClient
from ._dispatching import SMTPClient
from ._dispatching import plain_strategy
from ._email import Email
from ._exceptions import EmptyAttachmentFolderException
from ._exceptions import FilePathNotAttachmentException
from ._exceptions import InvalidAttachmentException
from ._exceptions import MailieException
from ._exceptions import SMTPException
from ._header import EmailHeader
from ._policy import POLICIES

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
    "HtmlContent",
    "EmptyAttachmentFolderException",
    "InvalidAttachmentException",
    "MailieException",
    "FilePathNotAttachmentException",
    "SMTPException",
    "plain_strategy",
]
