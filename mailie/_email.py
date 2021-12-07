from __future__ import annotations

import typing
from email.iterators import _structure  # type: ignore [attr-defined]
from email.message import EmailMessage
from pathlib import Path

from ._policy import Policies


class Email:
    """
    An encapsulation and representation of an email message.  At present only simple plaintext
    mails and multipart/alternative plain + html content mails are supported.  Client code should
    opt for using the email_factory rather than importing and instantiating `Email` instances
    themselves.  Only keyword arguments are supported in both `Email` and `email_factory` in a bid
    to build a more robust API.

        :param from_addr: (Required) The envelope sender of the email.  This is what is provided during the SMTP
        communication as part of the `MAIL FROM` part of the conversation later.

        :param to_addrs: (Required) The envelope recipient(s) of the email.  This is what is provided during the SMTP
        communication as part of the `RCPT TO` part of the conversation later.  to_addrs can be a single email address
        (str) or a list of email addresses.  In the event a single address is given, it will be converted to a list
        implicitly.

        :param policy: (Optional) ...

        :param cc: (Optional) ...

        :param bcc: (Optional) ...
                :: adding bcc explicitly in headers is acceptable as when sending they will not be visible.
                :: Prefer bcc=[..., ...] tho over a header encompassing bcc.

        :param subject: (Optional) ...

        :param text: (Optional) ...

        :param html: (Optional) ...

        :param charset: (Optional) ...

        :param headers: (Optional) ...

        :param attachments: (Optional) ...

        :param save_as_eml: (Default: False) ...


        Dev priorities:
            :: Complete delegation
            :: Refactor API
            :: Consider Builder pattern ?
            :: Use a tree and handle render so the data is in memory and accessible for assertions?
            :: Handle recursive `Email` types for subparts
            :: Do not couple sending of a mail, to the mail objects themselves
            :: Use the data model for header indexing etc?
            :: Implement factory pattern properly; rejig `Email` defaults`
            :: Fully type this code.
            :: Revisit logging, debugging etc
    """

    def __init__(
        self,
        *,
        from_addr: str,
        to_addrs: typing.Union[typing.List[str], str],
        policy: str,
        cc: typing.Optional[typing.List[str]] = None,
        bcc: typing.Optional[typing.List[str]] = None,
        subject: str = "",
        text: str = "",
        html: typing.Optional[str] = None,
        charset: typing.Optional[str],
        headers: typing.Optional[typing.List[EmailHeader]] = None,
        attachments: typing.Optional[typing.List[Path]] = None,
        save_as_eml: bool = False,
    ):
        if isinstance(to_addrs, str):
            to_addrs = [to_addrs]
        self.delegate = EmailMessage(Policies.get(policy))
        self.from_addr = from_addr
        self.to_addrs = to_addrs
        self.cc = cc or []
        self.bcc = bcc or []
        self.charset = charset
        self.all_recipients = self.to_addrs + self.cc + self.bcc
        self.subject = subject
        self.headers = self._build_headers(headers or ())
        for header in self.headers:
            self.delegate[header.field_name] = header.value
        self.delegate.set_content(text, subtype="plain")
        self.html = html
        if html:
            self.delegate.add_alternative(self.html, subtype="html")
        self.attachments = attachments
        self.save_as_eml = save_as_eml

    def _build_headers(self, optional: typing.Sequence[EmailHeader]) -> typing.List[EmailHeader]:
        required = self._get_required_headers()
        required.extend(optional)
        return required

    def _get_required_headers(self) -> typing.List[EmailHeader]:
        return [
            EmailHeader(field, value)
            for field, value in [("From", self.from_addr), ("To", ", ".join(self.to_addrs)), ("Subject", self.subject)]
        ]

    def render(self) -> None:
        # TODO: Implement better handling here; return a dictionary of parent:root nodes?
        _structure(self.delegate)

    def add_header(self, name: str, value: typing.Any, **params) -> Email:
        self.delegate.add_header(name, value, **params)
        return self

    def get_content_type(self) -> str:
        return self.delegate.get_content_type()

    def set_payload(self, payload: str, charset=None) -> Email:
        self.delegate.set_payload(payload, charset)
        return self

    def set_content(self, data: str, x: str) -> Email:
        self.delegate.set_content(data, x)
        return self

    def clear(self) -> Email:
        """
        Clears the headers and payload from the delegated `EmailMessage` messaged.
        If you want to retain non Content- headers, use `clear_content()` instead.
        """
        self.delegate.clear()
        return self

    def clear_content(self) -> Email:
        """
        Clears the payload and all non Content- headers.
        """
        self.delegate.clear_content()
        return self

    # ----- Data model specifics ----- #

    def __str__(self) -> str:
        return str(self.delegate)

    def __bytes__(self) -> bytes:
        return bytes(self.delegate)


class EmailHeader:
    def __init__(self, field_name: str, value: str):
        self.field_name = field_name
        self.value = value

    def __iter__(self):
        return iter((self.field_name, self.value))

    def __repr__(self) -> str:
        return f"Header=(field_name={self.field_name}, value={self.value})"

    @classmethod
    def from_string(cls, header: str, delimiter: str = ":") -> EmailHeader:
        return cls(*header.split(":"))


def email_factory(
    *,
    from_addr: str,
    to_addrs: typing.Union[typing.List[str], str],
    cc: typing.Optional[typing.List[str]] = None,
    bcc: typing.Optional[typing.List[str]] = None,
    subject: str = "",
    text: str = "",
    html: str = "",
    policy: str = "default",
    charset: typing.Optional[str] = None,
    headers: typing.Optional[typing.List[str]] = None,
    attachments: typing.Optional[typing.List[Path]] = None,
    save_as_eml: bool = False,
) -> Email:
    """
    A simple factory, for Emails.
    """
    if headers is None:
        headers = []
    resolved_headers = [EmailHeader.from_string(header) for header in headers]
    return Email(
        from_addr=from_addr,
        to_addrs=to_addrs,
        cc=cc,
        bcc=bcc,
        policy=policy,
        subject=subject,
        text=text,
        html=html,
        charset=charset,
        headers=resolved_headers,
        attachments=attachments,
        save_as_eml=save_as_eml,
    )
