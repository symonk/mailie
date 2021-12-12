import csv
import pathlib
import typing

from ._header import EmailHeader
from ._types import EMAIL_HEADER_ALIAS
from ._types import EMAIL_ITERABLE_ALIAS


def convert_strings_to_headers(headers: typing.Optional[EMAIL_HEADER_ALIAS] = None):
    """
    Given a list of strings (or possibly EmailHeader instances), return a new list
    that converts all the header data into `EmailHeader` instances.

    :param headers: (Optional) list of string headers (adhering to rfc-2822) or
    `EmailHeader` instances.  If headers is omitted, an empty list is returned.
    """
    if headers is None:
        return []
    new = []
    for header in headers:
        new.append(header if not isinstance(header, str) else EmailHeader.from_string(header))
    return new


def emails_to_list(emails: typing.Optional[EMAIL_ITERABLE_ALIAS] = None) -> typing.List[str]:
    """
    Given a single email address, or an iterable of emails, returns
    distinct email addresses in a new list.  if emails is not provided,
    an empty list is returned.

    :param emails: A single email address or iterable of emails.
    """
    if emails is None:
        return []
    return [emails] if isinstance(emails, str) else [email for email in set(emails)]


def check_is_email(email: str):
    ...


def unpack_recipients_from_csv(recipient_or_path: str) -> typing.List[str]:
    # TODO: Validate valid emails here - easier said than done me thinks;
    results = []
    recipient_or_path = recipient_or_path.strip()
    path = pathlib.Path(recipient_or_path)
    if path.is_file():
        with open(path, newline="") as file:
            email_reader = csv.reader(file, delimiter=",")
            for row in email_reader:
                for item in row:
                    results.append(item)
    else:
        results.append(recipient_or_path)
    return results
