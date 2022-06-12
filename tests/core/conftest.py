import pytest
from PIL import Image

from mailie import Email
from mailie import SyncClient


@pytest.fixture()
def render_checker():
    def parse(output: str):
        """
        # TODO: Consider this as part of the mail API, render(...) could do exactly this but programmatically
        # TODO: W/o leaving us parsing stdout?
        Splits the output of the email _structure(...).  Handled via tabbing
        """
        return list(map(str.strip, output.splitlines()))

    return parse


@pytest.fixture
def png_path(tmp_path):
    image = Image.new("RGB", (800, 1280), (255, 255, 255))
    path = f"{tmp_path}/image.png"
    image.save(path, "PNG")
    return path


@pytest.fixture
def html_multi_attach_mail(png_path):
    return Email(
        rcpt_to=["recip@recip.com"],
        mail_from="sender@onetwothree.com",
        subject="fooo!",
        headers=["one:two", "three:four"],
        text="plaintext content",
        html="<b> html content </b>",
        attachments=[png_path, png_path, png_path],
    )


@pytest.fixture(scope="function")
def email_factory():
    return Email


@pytest.fixture(scope="function")
def sync_client():
    return SyncClient
