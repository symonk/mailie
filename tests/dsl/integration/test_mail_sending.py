from mailie import Email
from mailie import HtmlContent
from mailie import SMTPClient


def test_email_example(mail_to_disk_server):
    mail = Email(
        to_addrs=["recip@recip.com"],
        from_addr="sender@onetwothree.com",
        subject="fooo!",
        headers=["one:two", "three:four"],
        text="plaintext content",
        html=HtmlContent("<b> html content </b>"),
    )
    SMTPClient(email=mail, port=9222).send()
