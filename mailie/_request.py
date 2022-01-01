import typing

from ._email import Email
from ._types import Auth


class Request:
    def __init__(self, *, email: Email, auth: typing.Optional[Auth] = None):
        self.email = email
        self.auth = auth
