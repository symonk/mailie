from mailie import Email
from mailie import SimpleDispatcher


def test_email_example(mail_to_disk_server):
    mail = Email(
        to_addrs=["recip@recip.com"],
        from_addr="sender@onetwothree.com",
        subject="fooo!",
        headers=["one:two", "three:four"],
        text="plaintext content",
        html="<b> html content </b>",
    )
    SimpleDispatcher(
        message=mail, host="localhost", port=9222
    ).send()  # Test for now using the background thread SMTP server
