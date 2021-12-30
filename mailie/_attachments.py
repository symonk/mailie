import mimetypes
import os
import pathlib
import typing
from dataclasses import dataclass

from ._exceptions import EmptyAttachmentFolderException
from ._exceptions import FilePathNotAttachmentException
from ._types import EMAIL_ATTACHMENT_PATH_ALIAS


@dataclass(repr=True, frozen=True, eq=True)
class FileAttachment:
    path: pathlib.Path
    name: str
    extension: str
    data: bytes

    @property
    def mime_types(self) -> typing.List[str]:
        """
        Attempts to resolve the main type and sub type of the file.  In the event that python cannot
        determine what it is; an application/octet-stream will be used.
        """
        c_type, encoding = mimetypes.guess_type(self.path)
        if c_type is None or encoding is not None:
            c_type = "application/octet-stream"  # Use a bag of bits as a fallback.
        return c_type.split("/", 1)
    
    
@typing.runtime_checkable
class Attachable(typing.Protocol):
    
    def generate(self, path: typing.Optional[EMAIL_ATTACHMENT_PATH_ALIAS] = None) -> typing.List[FileAttachment]:
        raise NotImplementedError
    
    
class AllFilesStrategy(Attachable):
    """
    A simple strategy for finding attachments.  This strategy is NOT recursive; only files found in the
    explicitly defined path directory will be considered (if the path is a dir and not an explicit file path).
    To recursively find all files in sub-folders; consider writing your own strategy.
    """
    
    def generate(self, path: typing.Optional[EMAIL_ATTACHMENT_PATH_ALIAS] = None) -> typing.List[FileAttachment]:
        """
        Accepts an iterable of string or PathLike, or a singular str or PathLike.  If a single element is provided
        it is converted into a list of length 1.  A rough overview of this functionality is outlined:
        """
        if path is None:
            return []
        paths = [pathlib.Path(p) for p in path] if not isinstance(path, (str, os.PathLike)) else [pathlib.Path(path)]
        return self._squash(paths)
    
    def _squash(self, paths: typing.List[pathlib.Path]) -> typing.List[FileAttachment]:
        """
        Squashes a list of pathlib.Path instances into their appropriate `FileAttachment` instances
        with appropriate exception handling.  Firstly each path is checked for a directory, if so
        then all files in that directory are generated as individual attachments.  If the path is
        a file, then it is generated as an attachment.  At present only files inside directories
        are generated, recursively looking in sub folders it not (yet) supported.

            :: If the path is a directory
                :: Find all files in the directory and generate attachments (raises if there are no files)
            :: If the path is a file
                :: Generate a `FileAttachment` for the file
                :: If the path provided is not a file, raises an exception
        """
        attachments = []
        for path in paths:
            if path.is_dir():
                non_recursive_files = [sub_path for sub_path in path.iterdir() if not sub_path.is_dir()]
                if not non_recursive_files:
                    raise EmptyAttachmentFolderException(
                        f"Directory: {path} does not contain any suitable files"
                    ) from None
                attachments.extend([self._generate_file_attachment(f) for f in non_recursive_files])
            elif path.is_file():
                attachments.append(self._generate_file_attachment(path))
            else:
                raise FilePathNotAttachmentException(f"path: {path} was not a directory or file.") from None
        return attachments

    @staticmethod
    def _generate_file_attachment(path: pathlib.Path) -> FileAttachment:
        """
        Given the `pathlib.Path` to a valid file on disk, build it into a `FileAttachment` instance
        and return it.
        """
        with open(path, "rb") as binary:
            return FileAttachment(
                path=path,
                name=path.name,
                extension=path.suffix,  # Todo: what about multiple extension files?
                data=binary.read(),
            )
        
class AsyncAllFilesStrategy(Attachable):
    
    def generate(self, path: typing.Optional[EMAIL_ATTACHMENT_PATH_ALIAS] = None) -> typing.List[FileAttachment]:
        """
        Accepts an iterable of string or PathLike, or a singular str or PathLike.  If a single element is provided
        it is converted into a list of length 1.  A rough overview of this functionality is outlined:
        """
        # Todo: Async implementation
        ...
    
    def _squash(self, paths: typing.List[pathlib.Path]) -> typing.List[FileAttachment]:
        """
        Squashes a list of pathlib.Path instances into their appropriate `FileAttachment` instances
        with appropriate exception handling.  Firstly each path is checked for a directory, if so
        then all files in that directory are generated as individual attachments.  If the path is
        a file, then it is generated as an attachment.  At present only files inside directories
        are generated, recursively looking in sub folders it not (yet) supported.

            :: If the path is a directory
                :: Find all files in the directory and generate attachments (raises if there are no files)
            :: If the path is a file
                :: Generate a `FileAttachment` for the file
                :: If the path provided is not a file, raises an exception
        """
        # Todo: Async implementation
        ...
    
    @staticmethod
    def _generate_file_attachment(path: pathlib.Path) -> FileAttachment:
        """
        Given the `pathlib.Path` to a valid file on disk, build it into a `FileAttachment` instance
        and return it.
        """
        # Todo: Async implementation
        ...
    
    
