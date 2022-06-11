from __future__ import annotations

import enum
import logging
import smtplib
import typing

from ._email import Email
from ._exceptions import MailieClientClosedException
from ._request import Request
from ._response import Response
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


@enum.unique
class ClientState(enum.Enum):
    NOT_YET_OPENED = 0  # The client has been instantiated but no requests have been dispatched.
    OPENED = 1  # The client is either inside the `with` context or has dispatched a request.
    CLOSED = 2  # The client has exited the `with` context or has been explicitly called `.close()`.


class MailieClient:
    """
    A simple mail client that supports SMTP, SMTP_SSL & LMTP as well as any subclasses of
    smtplib.SMTP.
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
        self.before: HOOKS_ALIAS = hooks.get("pre")
        self.after: HOOKS_ALIAS = hooks.get("post")

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

    def __enter__(self) -> MailieClient:
        self.delegate.__enter__()
        self.state = ClientState.OPENED
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.delegate.__exit__(exc_type, exc_val, exc_tb)
        self.state = ClientState.CLOSED

    def send(self, email: Email, auth: SMTP_AUTH_ALIAS = None) -> Response:
        """
        Send
        """
        if self.state.CLOSED:
            raise MailieClientClosedException("Cannot send mail, this client has been closed.  Open a new instance.")
        self.state = ClientState.OPENED
        request = Request(email=email, auth=auth)
        return Response(self.delegate.send_message(*request.email.smtp_arguments))

    def send_many(self) -> ...: ...

    def smtp_options(self):
        ...
