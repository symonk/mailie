import os
import re
import typing

from ._auth import Auth
from ._header import EmailHeader

EMAIL_ITERABLE_ALIAS = typing.Union[str, typing.Iterable[str]]
EMAIL_HEADER_ALIAS = typing.Union[typing.List[str], typing.List[EmailHeader]]
EMAIL_ATTACHMENT_PATH_ALIAS = typing.Union[typing.List[str], typing.List["os.PathLike[str]"], str, "os.PathLike[str]"]
EMAIL_ATTACHMENT_FILTER_ALIAS = typing.Union[str, re.Pattern]
SMTP_AUTH_ALIAS = Auth
