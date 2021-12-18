import functools
import logging
import smtplib
import ssl
import typing

from ._email import Email

# TODO: Future release; implement a plugin system, entry point and automatic registry for command line flags?
# TODO: e.g mailie --send-strategy some_plugin?
# TODO: Async support here; can we work around duplicating the API?

log = logging.getLogger(__name__)


class MailSender:
    # TODO: Study this stuff closely to see how we can have reusability.
    """https://docs.python.org/3/library/smtplib.html"""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 0,
        local_hostname: typing.Optional[str] = None,
        timeout: float = 30,
        source_address: typing.Optional[typing.Tuple[str, int]] = None,
        context: typing.Optional[ssl.SSLContext] = None,
        debug_level: int = 2,
    ) -> None:
        self.host = host
        self.port = port
        self.local_hostname = local_hostname
        self.timeout = timeout
        self.source_address = source_address
        self.debug_level = debug_level
        self.context = context
        self.sync_ctx = (
            functools.partial(
                smtplib.SMTP, self.host, self.port, self.local_hostname, self.timeout, self.source_address
            )
            if self.context is None
            else functools.partial(
                smtplib.SMTP_SSL,
                self.host,
                self.port,
                self.local_hostname,
                self.timeout,
                self.source_address,
                self.context,
            )
        )

    def send(self, mail: Email) -> Email:
        with self.sync_ctx() as connection:
            connection.set_debuglevel(self.debug_level)
            log.debug(connection.send_message(*mail.smtp_arguments))
        return mail

    async def asend(self, mail: Email) -> Email:
        # Todo: aiosmtplib for async contexts?
        ...
