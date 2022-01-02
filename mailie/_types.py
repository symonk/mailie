import os
import re
import typing
from email.charset import Charset
from email.message import Message

from ._auth import Auth
from ._header import EmailHeader

EMAIL_PAYLOAD_ALIAS = typing.Union[typing.List[Message], str, bytes]
EMAIL_CHARSET_ALIAS = typing.Union[Charset, str, None]
EMAIL_PARAMS_ALIAS = typing.Union[str, None, typing.Tuple[str, typing.Optional[str], str]]
EMAIL_PARAM_TYPE_ALIAS = typing.Union[str, typing.Tuple[typing.Optional[str], typing.Optional[str], str]]
EMAIL_HEADER_TYPE_ALIAS = typing.Any
EMAIL_ITERABLE_ALIAS = typing.Union[str, typing.Iterable[str]]
EMAIL_HEADER_ALIAS = typing.Union[typing.List[str], typing.List[EmailHeader]]
EMAIL_ATTACHMENT_PATH_ALIAS = typing.Union[typing.List[str], typing.List["os.PathLike[str]"], str, "os.PathLike[str]"]
EMAIL_ATTACHMENT_FILTER_ALIAS = typing.Union[str, re.Pattern]
SMTP_AUTH_ALIAS = Auth
