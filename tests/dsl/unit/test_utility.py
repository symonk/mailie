from mailie import EmailHeader
from mailie._utility import convert_strings_to_headers
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


def test_convert_strings_to_headers_empty() -> None:
    assert convert_strings_to_headers() == []


def test_convert_strings_to_headers_strings() -> None:
    data = ["foo:bar", EmailHeader.from_string("baz:boo")]
    result = convert_strings_to_headers(data)
    assert len(result) == 2
    assert isinstance(result, list)
    assert all(isinstance(header, EmailHeader) for header in result)
