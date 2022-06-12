from __future__ import annotations

import enum
import functools
import logging
import smtplib
import typing

from ._email import Email
from ._exceptions import MailieClientClosedException
from ._response import SMTPResponse
from ._types import EMAIL_FROM_TO_TYPES
from ._types import HOOKS_ALIAS
from ._types import SMTP_AUTH_ALIAS

# Todo: Async support here; can we work around duplicating the API?
# Todo: How do we encapsulate sending plain vs SSL?
# Todo: plaintext -> :: TLS :: -> plaintext upgraded via startTLS -> user defined commands?
# Todo: Handle `auth` & `login` in the conversation gracefully?
# Todo: Consider enforcing port 587 if starttls=True?
# Todo: Auth should be encapsulated; consider a function/callable too for user defined auth?
# Todo: This is massively WIP and quite an information overload; break it down into atomic pieces and tackle?
# Todo: Consider a 'transport' layer to split sync/async?
log = logging.getLogger(__name__)


def raise_on_closed(fn):
    """
    Guard the client code to ensure the underlying client has not already been closed.
    This should only be used on MailieClient instance methods.
    """

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        client: SyncClient = args[0]
        if client.state is ClientState.CLOSED:
            raise MailieClientClosedException("Cannot send mail, this client has been closed.  Open a new instance.")
        return fn(*args, **kwargs)

    return wrapper


@enum.unique
class ClientState(enum.Enum):
    NOT_YET_OPENED = 0  # The client has been instantiated but no requests have been dispatched.
    OPENED = 1  # The client is either inside the `with` context or has dispatched a request.
    CLOSED = 2  # The client has exited the `with` context or has been explicitly called `.close()`.


class SyncClient:
    """
    A simple mail client that supports SMTP, SMTP_SSL & LMTP as well as any subclasses of
    smtplib.SMTP.  This client is synchronous and will dispatch mails sequentially (if
    multiple are provided).
    """

    def __init__(
        self,
        *,
        host: str = "localhost",
        port: int = 25,
        local_hostname: typing.Optional[str] = None,
        source_address: typing.Optional[typing.Tuple[str, int]] = None,
        delegate_client: typing.Type[smtplib.SMTP] = smtplib.SMTP,
        timeout: float = 30.00,
        auth: typing.Optional[SMTP_AUTH_ALIAS] = None,
        debug: int = 0,
        hooks: typing.Optional[typing.Dict[str, typing.Callable[[typing.Any], typing.Any]]] = None,
        **client_kwargs,
    ) -> None:
        client_kwargs = self._merge_client_arguments(client_kwargs, host, port, local_hostname, source_address)
        self.debug = debug
        self.hooks = hooks
        self.timeout = timeout
        self.auth = auth
        self.delegate = delegate_client(**client_kwargs)
        self.state = ClientState.NOT_YET_OPENED
        self.delegate.set_debuglevel(self.debug)
        hooks = hooks or {}
        self.before: typing.Optional[HOOKS_ALIAS] = hooks.get("pre")
        self.after: typing.Optional[HOOKS_ALIAS] = hooks.get("post")

    @staticmethod
    def _merge_client_arguments(
        client_kw: typing.Dict[str, typing.Any],
        host: str,
        port: int,
        local_hostname: typing.Optional[str],
        source_address: typing.Optional[typing.Tuple[str, int]],
    ) -> typing.Dict[str, typing.Any]:
        """
        Merge the shared arguments into client specific ones and build a mapping that can be shovelled in
        during the client instantiation.
        """
        updates = {"host": host, "port": port, "local_hostname": local_hostname, "source_address": source_address}
        client_kw.update(**updates)
        return client_kw

    def __enter__(self) -> SyncClient:
        self.delegate.__enter__()
        self.state = ClientState.OPENED
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.delegate.__exit__(exc_type, exc_val, exc_tb)
        self.state = ClientState.CLOSED

    @raise_on_closed
    def send(
        self,
        *,
        email: Email,
        from_addr: typing.Optional[str] = None,
        to_addrs: typing.Optional[EMAIL_FROM_TO_TYPES] = None,
        mail_options: typing.Optional[typing.Sequence[str]] = None,
        rcpt_options: typing.Optional[typing.Sequence[str]] = None,
        enforce_all: bool = False,
    ) -> SMTPResponse:
        """
        Synchronously send an email.  from_addr & to_addrs are envelope senders, not to be confused with actual
        email TO and FROM headers.  SMTP communication cares NOT about an emails headers.

        :param from_addr: (optional) group of RFC-822 email addresses, uses the email message FROM header as fallback.
        :param to_addrs: (optional) An RFC-822 compliant email address, uses the email message TO header as fallback.
        :param email: Mailie `Email` object to send.
        :param mail_options: ESMTP options that should be passed with all MAIL FROM commands. (i.e 8bitmime)
        :param rcpt_options: ESMTP options that should be passed with all RCPT commands. (i.e DSN)
        :param enforce_all: Raise an exception if ALL to_addrs did not successfully receive the message.

        Right now mailie only supports high level sending APIs.  In future an Email obj will be 'aware' of the
        rcpt and mail options it can provide here.  Mailie only supports sending `Email` instances for a simpler
        API, sending raw bytes or strings containing ASCII is not officially supported though could be in the future.

        If there has been no EHLO or HELO command in the session, this will attempt ESMTP EHLO first, if ESMTP
        is supported by the server then message size and each of the specified options will be passed to it if
        the server broadcasts support such option(s).  If EHLO fails, HELO will be sent and ESMTP specific options
        will be suppressed by the underlying client.

        Because multiple to_addrs is permitted, if the mail is able to be successfully delivered to at least one of them
        no exception will be raised, if all recipients fail then an exception is raised.  To ensure that ALL recipients
        had no problems, `enforce_all=True` can be used.

        Typically, by default only ASCII is permitted for to/from addresses, however if mail_options contains
        `SMTPUTF8` then non ascii characters will be permitted (if the server supports it).
        """
        self.state = ClientState.OPENED
        send_args = {
            "msg": email.email_message,
            "from_addr": from_addr or email.mail_from,
            "to_addrs": to_addrs or email.rcpt_to,
            "mail_options": mail_options or (),
            "rcpt_options": rcpt_options or (),
        }
        # Todo: Decide what needs handled and what can be bubbled etc.
        try:
            return SMTPResponse(self.delegate.send_message(**send_args), enforce_all)
        # All recipients got refused.
        except smtplib.SMTPRecipientsRefused:
            raise
        # The server failed to respond to HELO (After EHLO)
        except smtplib.SMTPHeloError:
            raise
        # The server refused the from_address.
        except smtplib.SMTPSenderRefused:
            raise
        # The server replied with an unexpected error code (not recipient refusal)
        except smtplib.SMTPDataError:
            raise
        # SMTPUTF8 was provided in mail_options but the server does not support it.
        except smtplib.SMTPNotSupportedError:
            raise

    @raise_on_closed
    def smtp_options(self, name: str = "") -> typing.Dict[str, str]:
        """
        Perform a check for the (E)smtp options available on the host.  If name is empty then
        the fully qualified domain name of the local host.
        """
        self.delegate.ehlo(name)
        return self.delegate.esmtp_features
