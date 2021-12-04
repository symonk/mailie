from .__version__ import VERSION
from ._email import EmailHeader
from ._email import email_factory
from ._policy import Policies

__all__ = ["email_factory", "Policies", "VERSION", "EmailHeader"]
