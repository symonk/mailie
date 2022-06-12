import logging

import importlib_metadata

from ._attachments import Attachable
from ._attachments import FileAttachment
from ._client import SyncClient
from ._email import Email
from ._exceptions import EmptyAttachmentFolderException
from ._exceptions import FilePathNotAttachmentException
from ._exceptions import InvalidAttachmentException
from ._exceptions import MailieException
from ._exceptions import SMTPException
from ._policy import POLICIES
from ._response import SMTPResponse

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


# importlib_metadata is necessary here for backwards compat with mkdocs.
version = importlib_metadata.version("mailie")  # type: ignore [attr-defined]


__all__ = [
    "Email",
    "POLICIES",
    "version",
    "FileAttachment",
    "Attachable",
    "SyncClient",
    "SMTPResponse",
    "EmptyAttachmentFolderException",
    "InvalidAttachmentException",
    "MailieException",
    "FilePathNotAttachmentException",
    "SMTPException",
]
