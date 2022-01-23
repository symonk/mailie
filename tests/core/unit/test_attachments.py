import pytest

from mailie import Email
from mailie import EmptyAttachmentFolderException
from mailie import FilePathNotAttachmentException


def test_attachments_empty_directory(tmp_path) -> None:
    with pytest.raises(EmptyAttachmentFolderException):
        Email(mail_from="foo@bar.com", rcpt_to="hi@bye.com", attachments=tmp_path)


def test_madeup_directory() -> None:
    with pytest.raises(FilePathNotAttachmentException) as exc:
        Email(mail_from="foo@bar.com", rcpt_to="hi@bye.com", attachments="foo/bar/bin/baz/")
    assert exc.value.args[0] == "path: foo/bar/bin/baz was not a directory or file."


def test_single_attachment(png_path) -> None:
    Email(mail_from="foo@bar.com", rcpt_to="hi@bye.com", attachments=png_path)


def test_inline_attachment(png_path) -> None:
    Email(
        mail_from="foo@bar.com",
        rcpt_to="one@two.com",
        html="""
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
    )
