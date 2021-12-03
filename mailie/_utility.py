import csv
import pathlib
import typing


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
