import typing

from ._header import EmailHeader

EMAIL_ITERABLE_ALIAS = typing.Union[str, typing.Iterable[str]]
EMAIL_HEADER_ALIAS = typing.Union[typing.List[str], typing.List[EmailHeader]]
