import logging

import pkg_resources

from ._attachments import Attachable
from ._attachments import FileAttachment
from ._client import AsyncClient
from ._client import Client
from ._email import Email
from ._exceptions import EmptyAttachmentFolderException
from ._exceptions import FilePathNotAttachmentException
from ._exceptions import InvalidAttachmentException
from ._exceptions import MailieException
from ._exceptions import SMTPException
from ._header import EmailHeader
from ._policy import POLICIES
from ._request import Request
from ._response import Response

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


version = pkg_resources.get_distribution("mailie")


__all__ = [
    "Email",
    "POLICIES",
    "version",
    "EmailHeader",
    "Client",
    "AsyncClient",
    "FileAttachment",
    "Attachable",
    "Request",
    "Response",
    "EmptyAttachmentFolderException",
    "InvalidAttachmentException",
    "MailieException",
    "FilePathNotAttachmentException",
    "SMTPException",
]
