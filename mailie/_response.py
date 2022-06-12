import typing


class SMTPResponse:
    """
    An encapsulation of SMTP responses.  This is a multi-recipient response and stores all information
    for all email addresses attempted.
    """

    def __init__(self, result: typing.Dict[typing.Any, typing.Any], enforce_all: bool) -> None:
        self.enforce_all = enforce_all
        self.result = result
