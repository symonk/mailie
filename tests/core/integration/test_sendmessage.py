from pytest_mock import MockerFixture


def test_send_message_from_addr(integration_mail_server, email_factory, sync_client, mocker: MockerFixture):
    mock_smtp = mocker.patch("smtplib.SMTP.send_message")
    with sync_client(port=9222) as client:
        email = email_factory(mail_from="foo@bar.com", rcpt_to=("a@one.com", "b@two.com"))
        client.send(email=email, from_addr="fake@stub.com")
        assert mock_smtp.called
        assert mock_smtp.call_args[-1]['from_addr'] == "fake@stub.com"
