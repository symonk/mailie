"""
:: MailException
    :: InvalidAttachmentException
        :: FilePathNotAttachmentException
    :: SMTPException
"""


class MailieException(Exception):
    """Generic Mailie exception, everything will stem from this"""


class InvalidAttachmentException(MailieException):
    """Raised when an email is provided an attachment path that is non existent or problematic"""


class FilePathNotAttachmentException(InvalidAttachmentException):
    """Raised when the file path given for an attachment does not exist on disk"""


class EmptyAttachmentFolderException(InvalidAttachmentException):
    """Raised when an attachment path provided is a directory; however no files exist in the directory"""


class SMTPException(MailieException):
    """Raised when an exception occurs during the SMTP conversation with the smtp server"""


class StartTLSNotSupportedException(SMTPException):
    """Raised when starttls() fails for the smtp connection as the server does not support the extension"""


class MailieClientClosedException(MailieException):
    """Raised when attempting to use an instance of the mailie client to send mail after it has been closed"""
