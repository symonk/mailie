from mailie import Email


def test_mail_sending(null_smtp_server) -> None:
    Email(subject="foobar", frm="simon@test.com", to="nomis@testing.com").set_payload("My Message!").send()
