from mailie import Email


def test_subject_via_list_in_headers() -> None:
    email = Email(mail_from="foo@bar.com", rcpt_to="baz@foo.com", headers=["Subject:AsList"])
    assert email["Subject"] == "AsList"


def test_subject_via_mapping_in_headers() -> None:
    email = Email(mail_from="foo@bar.com", rcpt_to="baz@foo.com", headers={"Subject": "AsList"})
    assert email["Subject"] == "AsList"


def test_subject_as_subject_kwarg() -> None:
    email = Email(mail_from="foo@bar.com", rcpt_to="baz@foo.com", subject="KeywordArg")
    assert email["Subject"] == "KeywordArg"
