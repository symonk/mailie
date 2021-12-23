import logging
import smtplib
import typing

from ._email import Email

# TODO: Future release; implement a plugin system, entry point and automatic registry for command line flags?
# TODO: e.g mailie --send-strategy some_plugin?
# TODO: Async support here; can we work around duplicating the API?

log = logging.getLogger(__name__)


class SMTPClient:
    """
    :param hooks: (Optional) A mapping of callable instances for executing user defined code at various
        stages of the SMTP flow.  Currently the following hooks are supported:
            :: 'post' - Invoked after sending the email (successfully).
            This permits user defined code to hook and handle post processing before exiting.  Some useful
            examples of these hooks could be to write the sent email to .eml, or update some other system.
            Callables set for 'post' should adhere to the following interface:

                def post(email: Email, result: Dict) -> Email:
                    ...

            `email` and `result` are automatically injected into the callable after the mail has been sent.
            email is the instance of `Email` that was built and `result` is the dictionary of errors from
            calling `send_message(...)` in aiosmtplib.
    """

    # Todo: How do we encapsulate sending plain vs SSL?

    def __init__(
        self,
        sending_strategy: typing.Callable,  # type: ignore [type-arg]
        hooks: typing.Optional[typing.Callable[[Email, typing.Dict[typing.Any, typing.Any]], None]] = None,
    ) -> None:
        self.sending_strategy = sending_strategy
        self.hooks = hooks

    def send(self) -> Email:
        return self.sending_strategy()  # type: ignore [no-any-return]


class ASyncSMTPClient:
    def __init__(
        self,
        sending_strategy: typing.Callable,  # type: ignore [type-arg]
        hooks: typing.Optional[typing.Callable[[Email, typing.Dict[typing.Any, typing.Any]], None]] = None,
    ) -> None:
        self.sending_strategy = sending_strategy
        self.hooks = hooks

    async def send(self) -> Email:
        return await self.sending_strategy()  # type: ignore [no-any-return]


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
        connection.set_debuglevel(debug)
        log.debug(connection.send_message(*email.smtp_arguments))
