import pytest


@pytest.mark.skip
def test_send_message_rcp_to(integration_mail_server, email_factory, sync_client, mocker):
        mock_smtp = mocker.patch("smtplib.SMTP.send_message", autospec=True)
        mock_smtp.return_value = {}
        with sync_client() as client:
            email = email_factory(mail_from="foo@bar.com", rcpt_to=("a@one.com", "b@two.com"))
            result = client.send(msg=email)
            raise Exception(result)


