import csv
import pathlib
import typing

from ._types import EMAIL_ITERABLE_ALIAS


def split_headers_per_rfc(
    header_data: typing.Optional[typing.Iterable[str]] = None, delimiter: str = ":"
) -> typing.List[typing.List[str]]:
    """
    Given an iterable or RFC compliant header strings, convert them into tuples of header field:header value pairs
    ready for use within a `mailie.Email` instance.  By default using the RFC compliant colon delimiter.
    """
    if header_data is None:
        return []
    return [header.rsplit(delimiter, maxsplit=1) for header in header_data]


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
    # TODO: Validate valid emails here - easier said than done me thinks;
    ...


def unpack_recipients_from_csv(recipient_or_path: str) -> typing.List[str]:
    """
    Given a valid path to a `.csv` file containing recipient data; parse the
    file and generate a list of recipient email addresses.  If the recipient
    is not a valid path, it is treated as an actual email address and added
    to the results.

    # Todo: Treating non files as email addresses seems a little odd.
    """
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
