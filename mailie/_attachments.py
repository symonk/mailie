import typing
from dataclasses import dataclass

from ._types import EMAIL_ATTACHMENT_PATH_ALIAS


@dataclass(repr=True, frozen=True, eq=True)
class FileAttachment:
    def __init__(self) -> None:
        ...


class Attachable(typing.Protocol):
    def generate(self) -> typing.Iterable[FileAttachment]:
        ...


class AttachmentBuilder(Attachable):
    def __init__(self, path: EMAIL_ATTACHMENT_PATH_ALIAS) -> None:
        self.path = path

    def generate(self) -> typing.List[FileAttachment]:
        ...
