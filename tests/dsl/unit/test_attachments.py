import pytest

from mailie import Email
from mailie import EmptyAttachmentFolderException
from mailie import FilePathNotAttachmentException


def test_attachments_empty_directory(tmp_path) -> None:
    with pytest.raises(EmptyAttachmentFolderException):
        Email(from_addr="foo@bar.com", to_addrs="hi@bye.com", attachments_path=tmp_path)


def test_madeup_directory() -> None:
    with pytest.raises(FilePathNotAttachmentException) as exc:
        Email(from_addr="foo@bar.com", to_addrs="hi@bye.com", attachments_path="foo/bar/bin/baz/")
    assert exc.value.args[0] == "path: foo/bar/bin/baz was not a directory or file."
