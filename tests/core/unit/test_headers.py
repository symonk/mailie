from mailie import Email


def test_subject_via_list_in_headers() -> None:
    email = Email(from_addr="foo@bar.com", to_addrs="baz@foo.com", headers=["Subject:AsList"])
    assert email["Subject"] == "AsList"


def test_subject_via_mapping_in_headers() -> None:
    email = Email(from_addr="foo@bar.com", to_addrs="baz@foo.com", headers={"Subject": "AsList"})
    assert email["Subject"] == "AsList"


def test_subject_as_subject_kwarg() -> None:
    email = Email(from_addr="foo@bar.com", to_addrs="baz@foo.com", subject="KeywordArg")
    assert email["Subject"] == "KeywordArg"
