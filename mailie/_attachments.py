import os
import pathlib
import typing
from dataclasses import dataclass

from ._exceptions import EmptyAttachmentFolderException
from ._exceptions import FilePathNotAttachmentException
from ._types import EMAIL_ATTACHMENT_PATH_ALIAS


@dataclass(repr=True, frozen=True, eq=True)
class FileAttachment:
    def __init__(self) -> None:
        ...


class AttachmentStrategy:
    """
    A simple strategy for finding attachments.  This strategy is NOT recursive; only files found in the
    explicitly defined path directory will be considered (if the path is a dir and not an explicit file path).
    To recursively find all files in sub-folders; consider writing your own strategy.
    """

    def __call__(self, path: typing.Optional[EMAIL_ATTACHMENT_PATH_ALIAS] = None) -> typing.List[FileAttachment]:
        """
        Accepts an iterable of string or PathLike, or a singular str or PathLike.  If a single element is provided
        it is converted into a list of length 1.  A rough overview of this functionality is outlined:

            :: If path is None, en empty list is returned.
            :: If path is a single string or PathLike
                :: If `path` is a folder, grab all the files in that directory and build them into `FileAttachment`s.
                :: Else the file path is converted into a list [path]
            :: For each path in the paths list
                :: If `path` is a folder, grab all the files in that directory and build them into `FileAttachment`s.
                :: If `path` is a singular file, grab the file and build it into a `FileAttachment`
        """
        files: typing.List[FileAttachment] = []
        if path is None:
            return files

        paths = path if not isinstance(path, (str, os.PathLike)) else [path]
        for p in paths:
            p = pathlib.Path(p)
            if p.is_dir():
                # Convert all files in the directory to `FileAttachment`
                dir_files = list(p.iterdir())
                if not dir_files:
                    raise EmptyAttachmentFolderException(f"Directory: {p} does not contain any files")
                files.extend(map(lambda f: self._generate_file_attachment(f), p.iterdir()))
                continue
            elif p.is_file():
                # Convert the file into a `FileAttachment`
                files.append(self._generate_file_attachment(p))
            else:
                raise FilePathNotAttachmentException(f"path: {p} was not a directory or file.")
        return files

    @staticmethod
    def _generate_file_attachment(path: pathlib.Path) -> FileAttachment:
        """
        Given the `pathlib.Path` to a valid file on disk, build it into a `FileAttachment` instance
        and return it.
        """
        f = FileAttachment()
        return f
