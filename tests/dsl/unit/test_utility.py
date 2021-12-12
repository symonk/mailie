from mailie._utility import emails_to_list


def test_email_to_list_with_email() -> None:
    assert emails_to_list("foo@bar.com") == ["foo@bar.com"]


def test_email_to_list_with_iterable() -> None:
    data = ("one@domain.com", "two@domain.com", "three@domain.com")
    assert isinstance(emails_to_list(data), list)
    assert len(emails_to_list(data)) == 3


def test_email_to_list_duplicates() -> None:
    data = ("one@domain.com", "two@domain.com", "three@domain.com", "one@domain.com")
    assert emails_to_list(data).count("one@domain.com") == 1


def test_email_to_list_none() -> None:
    assert emails_to_list() == []
