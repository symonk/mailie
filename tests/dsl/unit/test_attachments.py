import pytest

from mailie import Email
from mailie import EmptyAttachmentFolderException
from mailie import FilePathNotAttachmentException
from mailie import HtmlContent


def test_attachments_empty_directory(tmp_path) -> None:
    with pytest.raises(EmptyAttachmentFolderException):
        Email(from_addr="foo@bar.com", to_addrs="hi@bye.com", attachments=tmp_path)


def test_madeup_directory() -> None:
    with pytest.raises(FilePathNotAttachmentException) as exc:
        Email(from_addr="foo@bar.com", to_addrs="hi@bye.com", attachments="foo/bar/bin/baz/")
    assert exc.value.args[0] == "path: foo/bar/bin/baz was not a directory or file."


def test_single_attachment(png_path) -> None:
    Email(from_addr="foo@bar.com", to_addrs="hi@bye.com", attachments=png_path)


def test_inline_attachment(png_path) -> None:
    Email(
        from_addr="foo@bar.com",
        to_addrs="one@two.com",
        html=HtmlContent(
            """
    <html>
  <head></head>
  <body>
    <p>Salut!</p>
    <p>Cela ressemble à un excellent
        <a href="http://www.yummly.com/recipe/Roasted-Asparagus-Epicurious-203718">
            recipie
        </a> déjeuner.
    </p>
    <img src="cid:{0}" />
  </body>
</html>
    """,
            png_path,
        ),
    )
