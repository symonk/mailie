from __future__ import annotations

import enum
import logging
import smtplib
import ssl
import types
import typing

from ._email import Email
from ._request import Request
from ._response import Response
from ._types import SMTP_AUTH_ALIAS

# Todo: Async support here; can we work around duplicating the API?
# Todo: How do we encapsulate sending plain vs SSL?
# Todo: plaintext -> :: TLS :: -> plaintext upgraded via startTLS -> user defined commands?
# Todo: Handle `auth` & `login` in the conversation gracefully?
# Todo: Consider enforcing port 587 if starttls=True?
# Todo: Auth should be encapsulated; consider a function/callable too for user defined auth?
# Todo: This is massively WIP and quite an information overload; break it down into atomic pieces and tackle?
log = logging.getLogger(__name__)


@enum.unique
class ClientState(enum.Enum):
    NOT_YET_OPENED = 0  # The client has been instantiated but no requests have been dispatched.
    OPENED = 1  # The client is either inside the `with` context or has dispatched a request.
    CLOSED = 2  # The client has exited the `with` context or has been explicitly called `.close()`.


class BaseSMTPClient:
    """
    A Base SMTPClient.
    """

    def __init__(
        self,
        *,
        host: str = "localhost",
        port: int = 25,
        local_hostname: typing.Optional[str] = None,
        timeout: float = 30.00,
        source_address: typing.Optional[typing.Tuple[str, int]] = None,
        debug: int = 0,
        hooks: typing.Optional[typing.Dict[str, typing.Callable[[typing.Any], typing.Any]]] = None,
        auth: typing.Optional[SMTP_AUTH_ALIAS] = None,
        use_starttls: bool = False,
        use_tls: bool = False,
        tls_context: typing.Optional[ssl.SSLContext] = None,
    ) -> None:
        self.host = host
        self.port = port
        self.local_hostname = local_hostname
        self.timeout = timeout
        self.source_address = source_address
        self.debug = debug
        self.hooks = hooks or {}
        self.auth = auth
        self.use_starttls = use_starttls if not use_tls else False  # Using tls and starttls will use tls as priority.
        self.use_tls = use_tls
        self.tls_context = tls_context
        self._delegate_client: smtplib.SMTP = (
            smtplib.SMTP(
                host=self.host,
                port=self.port,
                local_hostname=self.local_hostname,
                timeout=self.timeout,
                source_address=self.source_address,
            )
            if not use_tls
            else smtplib.SMTP_SSL(
                host=self.host,
                port=self.port,
                local_hostname=self.local_hostname,
                timeout=self.timeout,
                source_address=self.source_address,
                context=self.tls_context,
            )
        )
        self._state = ClientState.NOT_YET_OPENED

    @property
    def is_closed(self) -> bool:
        return self._state == ClientState.CLOSED

    @property
    def is_open(self) -> bool:
        return self._state == ClientState.OPENED

    @property
    def pre_hook(self) -> typing.Optional[typing.Callable[[typing.Any], typing.Any]]:
        return self.hooks.get("pre")

    @property
    def post_hook(self) -> typing.Optional[typing.Callable[[typing.Any], typing.Any]]:
        return self.hooks.get("post")


class Client(BaseSMTPClient):
    """
    A simple synchronous SMTP client.  Client code should typically interact with `send(...)` however
    if you wish to have more fine-grained control, building a `Request` object manually and passing it
    to `dispatch_request(request=request)` is the way to handle that.  `send(...)` under the hood creates
    its own `mailie.Request` instance implicitly.  All SMTP communication will yield a `mailie.Response`
    instance.
    """

    def __init__(
        self,
        *,
        host: str = "localhost",
        port: int = 25,
        local_hostname: typing.Optional[str] = None,
        timeout: float = 30.00,
        source_address: typing.Optional[typing.Tuple[str, int]] = None,
        debug: int = 0,
        hooks: typing.Optional[typing.Dict[str, typing.Callable[[typing.Any], typing.Any]]] = None,
        auth: typing.Optional[SMTP_AUTH_ALIAS] = None,
        use_starttls: bool = False,
        use_tls: bool = False,
        tls_context: typing.Optional[ssl.SSLContext] = None,
    ) -> None:
        super().__init__(
            host=host,
            port=port,
            local_hostname=local_hostname,
            timeout=timeout,
            source_address=source_address,
            debug=debug,
            hooks=hooks,
            auth=auth,
            use_starttls=use_starttls,
            use_tls=use_tls,
            tls_context=tls_context,
        )

    def __enter__(self) -> Client:
        self._delegate_client.__enter__()
        return self

    def __exit__(
        self,
        exc_type: typing.Optional[typing.Type[BaseException]] = None,
        exc_val: typing.Optional[BaseException] = None,
        exc_tb: typing.Optional[types.TracebackType] = None,
    ) -> None:
        self._delegate_client.__exit__(exc_type, exc_val, exc_tb)
        self._state = ClientState.CLOSED

    def __del__(self) -> None:
        try:
            self._delegate_client.close()
        except Exception:
            pass
        finally:
            self._state = ClientState.CLOSED

    def set_debug_level(self, level: int) -> Client:
        self._delegate_client.set_debuglevel(level)
        return self

    def send(self, *, email: Email, auth: typing.Optional[SMTP_AUTH_ALIAS] = None) -> Response:
        """
        The public API of our SMTP communication, client code should primarily deal with calling
        this method, auth can be overridden on a per request basis and if provided here will
        take priority over what was passed into auth= for the session.  This allows changing
        auth with the same underlying client.
        """
        if self._state == ClientState.CLOSED:
            raise RuntimeError("Cannot send a mail as this client has been closed.")
        self._state = ClientState.OPENED
        return self.dispatch_request(request=self._build_request(email=email, auth=auth))

    def turret(
        self, *, email: Email, auth: typing.Optional[SMTP_AUTH_ALIAS] = None, count: int = 1
    ) -> typing.List[Response]:
        """
        Turret in the same mail a number of times.  This is a sequential sync operation, in order to perform turreting
        in a faster more efficient manner; consider using an `AsyncClient`.
        """
        return [self.send(email=email, auth=auth) for _ in range(count)]

    def fetch_esmtp_options(self, name: str = "") -> typing.Dict[str, str]:
        """
        Perform a check for the (E)smtp options available on the host; name if empty will use the
        FQDN of localhost.
        """
        self._delegate_client.ehlo(name)
        return self._delegate_client.esmtp_features

    def dispatch_request(self, *, request: Request) -> Response:
        self.set_debug_level(self.debug)
        return Response(self._delegate_client.send_message(*request.email.smtp_arguments))

    @staticmethod
    def _build_request(*, email: Email, auth: typing.Optional[SMTP_AUTH_ALIAS] = None) -> Request:
        return Request(email=email, auth=auth)
    
    def is_connected(self) -> bool:
        try:
            status = self._delegate_client.noop()[0]
        except:
            status = -1
        return True if status == 250 else False


class AsyncClient(BaseSMTPClient):
    def __init__(
        self,
        *,
        host: str = "localhost",
        port: int = 25,
        local_hostname: typing.Optional[str] = None,
        timeout: float = 30.00,
        source_address: typing.Optional[typing.Tuple[str, int]] = None,
        debug: int = 0,
        hooks: typing.Optional[typing.Dict[str, typing.Callable[[typing.Any], typing.Any]]] = None,
        auth: typing.Optional[SMTP_AUTH_ALIAS] = None,
        use_starttls: bool = False,
        use_tls: bool = False,
        tls_context: typing.Optional[ssl.SSLContext] = None,
    ) -> None:
        super().__init__(
            host=host,
            port=port,
            local_hostname=local_hostname,
            timeout=timeout,
            source_address=source_address,
            debug=debug,
            hooks=hooks,
            auth=auth,
            use_starttls=use_starttls,
            use_tls=use_tls,
            tls_context=tls_context,
        )

    async def send(self, *, email: Email, hostname: str = "localhost", port: int = 25) -> Email:
        ...

    async def __aenter__(self) -> AsyncClient:
        return self

    async def __aexit__(*args, **kw) -> None:
        ...
