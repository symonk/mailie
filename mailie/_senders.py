import smtplib

import typer

from ._email import Email


class Dispatcher:
    # TODO: Study this stuff closely to see how we can have reusability.
    """https://docs.python.org/3/library/smtplib.html"""


class SimpleDispatcher(Dispatcher):  # TODO: Terrible name; improve it.
    def __init__(
        self,
        *,
        message: Email,
        host: str = "",
        port: int = 0,
        # Todo: More options.
    ) -> None:
        self.message = message
        self.host = host
        self.port = port

    def send(self) -> Email:
        # send_message does not transmit any Bcc or Resent-Bcc headers that may appear in msg
        with smtplib.SMTP(self.host, port=self.port) as smtp:
            # Do not change this to use `smtp.sendmail(...)`.
            result = smtp.send_message(*self.message.smtp_arguments())
            typer.secho(result, fg=typer.colors.GREEN, bold=True)
        return self.message


class SSLDispatcher(Dispatcher):
    ...
