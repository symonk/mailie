import functools
import logging
import smtplib
import ssl
import typing

from ._email import Email
from ._exceptions import StartTLSNotSupportedException

# TODO: Future release; implement a plugin system, entry point and automatic registry for command line flags?
# TODO: e.g mailie --send-strategy some_plugin?
# TODO: Async support here; can we work around duplicating the API?

log = logging.getLogger(__name__)


class SMTPClient:
    # Todo: How do we encapsulate sending plain vs SSL?
    # Todo: plaintext -> :: TLS :: -> plaintext upgraded via startTLS -> user defined commands?
    # Todo: Handle `auth` & `login` in the conversation gracefully?
    # Todo: Consider enforcing port 587 if starttls=True?

    def __init__(
        self,
        email: Email,
        *,
        host: str = "localhost",
        port: int = 25,
        local_hostname: typing.Optional[str] = None,
        timeout: float = 30.00,
        source_address: typing.Optional[typing.Tuple[str, int]] = None,
        debug: int = 2,
        starttls: bool = False,
        tls: bool = False,
        auth: typing.Optional[typing.Tuple[str, str]] = None,
        ssl_context: typing.Optional[ssl.SSLContext] = None,
        hooks: typing.Optional[typing.Callable[[Email, typing.Dict[typing.Any, typing.Any]], None]] = None,
    ) -> None:
        self.email = email
        self.host = host
        self.port = port
        self.local_hostname = local_hostname
        self.timeout = timeout
        self.source_address = source_address
        self.debug = debug
        self.starttls = starttls if tls is False else False  # tls takes priority over starttls for security reasons.
        self.tls = tls
        self.auth = auth
        self.ssl_context = ssl_context or ssl.create_default_context()  # useful for starttls & tls.
        self.hooks = hooks
        self._client = functools.partial(smtplib.SMTP_SSL, context=self.ssl_context) if self.tls else smtplib.SMTP

    def send(self) -> Email:
        with self._client(  # type: ignore [operator]
            host=self.host,
            port=self.port,
            local_hostname=self.local_hostname,
            timeout=self.timeout,
            source_address=self.source_address,
        ) as connection:
            if self.starttls:
                try:
                    stls_result = connection.starttls(context=self.ssl_context)
                    log.debug(f"upgrading connection via starttls result: {stls_result}")
                except smtplib.SMTPNotSupportedError:
                    raise StartTLSNotSupportedException(f"StartTLS not supported on: {self.host}:{self.port}") from None
            connection.set_debuglevel(self.debug)
            log.debug(connection.send_message(*self.email.smtp_arguments))
            return self.email


class AsyncSMTPClient:
    ...
