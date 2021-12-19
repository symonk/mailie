import typing
from dataclasses import dataclass

from ._types import EMAIL_ATTACHMENT_PATH_ALIAS


@dataclass(repr=True, frozen=True, eq=True)
class FileAttachment:
    def __init__(self) -> None:
        ...


class AttachmentStrategy:
    """
    A simple strategy for finding attachments.  Supports filtering files
    """

    def __call__(self, path: typing.Optional[EMAIL_ATTACHMENT_PATH_ALIAS] = None) -> typing.List[FileAttachment]:
        """
        Given a list of file paths, builds a container (list) of the actual attachment files,
        ready to be attached to an email.  If attachment_paths is omitted, an empty list is
        returned.  If a directory path is provided all files in the given directory are treated
        as attachments otherwise the explicit paths provided will each be iterated and attached.
        If any of the paths in the list provided are infact folders; all files inside those folders
        will also be checked for any attachments and all will be included.
        """

        #  Todo: Where does inline & content disposition fit into this API.
