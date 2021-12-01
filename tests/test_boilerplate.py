from mailie import EmailFactory


def test_mail_sending(null_smtp_server) -> None:
    EmailFactory.create(subject="foobar", frm="simon@test.com", to="nomis@testing.com").set_payload("My Message!")
