from mailie import Client
from mailie import Email


def test_email_example(mail_to_disk_server):
    mail = Email(
        rcpt_to=["recip@recip.com"],
        mail_from="sender@onetwothree.com",
        subject="fooo!",
        headers=["one:two", "three:four"],
        text="plaintext content",
        html="<b> html content </b>",
    )
    Client(port=9222).send(email=mail)


def test_email_boundaries(mail_to_disk_server, html_multi_attach_mail):
    Client(port=9222).send(email=html_multi_attach_mail)


def test_turreting(mail_to_disk_server, html_multi_attach_mail):
    with Client(port=9222) as client:
        client.turret(email=html_multi_attach_mail, count=4)


def test_esmtp_options(mail_to_disk_server):
    expected = {"8bitmime": "", "help": "", "size": "33554432"}
    options = Client(port=9222).fetch_esmtp_options()
    assert expected == options
