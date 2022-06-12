from mailie import Email
from mailie import SyncClient


def test_email_example(integration_mail_server):
    mail = Email(
        rcpt_to=["recip@recip.com"],
        mail_from="sender@onetwothree.com",
        subject="fooo!",
        headers=["one:two", "three:four"],
        text="plaintext content",
        html="<b> html content </b>",
    )
    SyncClient(port=9222).send(email=mail)


def test_email_boundaries(integration_mail_server, html_multi_attach_mail):
    SyncClient(port=9222).send(email=html_multi_attach_mail)


def test_esmtp_options(integration_mail_server):
    expected = {"8bitmime": "", "help": "", "size": "33554432"}
    options = SyncClient(port=9222).smtp_options()
    assert expected == options
