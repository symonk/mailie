import logging
import smtplib
import typing

from ._email import Email

# TODO: Future release; implement a plugin system, entry point and automatic registry for command line flags?
# TODO: e.g mailie --send-strategy some_plugin?
# TODO: Async support here; can we work around duplicating the API?

log = logging.getLogger(__name__)


class SMTPClient:
    # Todo: How do we encapsulate sending plain vs SSL?

    def __init__(self, sending_strategy: typing.Callable) -> None:
        self.sending_strategy = sending_strategy

    def send(self) -> Email:
        return self.sending_strategy()


class ASyncSMTPClient:
    def __init__(self, sending_strategy: typing.Callable) -> None:
        self.sending_strategy = sending_strategy

    async def send(self) -> Email:
        return await self.sending_strategy()


def plain_strategy(
    email: Email,
    *,
    host: str = "localhost",
    port: int = 25,
    local_hostname: typing.Optional[str] = None,
    timeout: float = 30.00,
    source_address: typing.Optional[typing.Tuple[str, int]] = None,
    debug: int = 2,
):
    with smtplib.SMTP(host, port, local_hostname, timeout, source_address) as connection:
        connection.set_debuglevel(debuglevel=2)
        log.debug(connection.send_message(*email.smtp_arguments))
