from __future__ import annotations

import smtplib
import typing
from email.iterators import _structure  # type: ignore [attr-defined]
from email.message import EmailMessage
from pathlib import Path

import typer

from ._policy import Policies


class Email:
    """
    An Email.  For now we want to support a simple plaintext & html relative mail.  That is the focus
    to iron out the API then build on more in depth structures going forward.  Client code should create
    email objects through the `email_factory` ideally.

        :: adding bcc explicitly in headers is acceptable as when sending they will not be visible.
        :: Prefer bcc=[..., ...] tho over a header encompassing bcc.

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
            ::
    """

    def __init__(
        self,
        *,
        frm: str,
        to: typing.List[str],
        policy: str,
        cc: typing.Optional[typing.List[str]] = None,
        bcc: typing.Optional[typing.List[str]] = None,
        subject: str = "",
        text: str = "",
        html: typing.Optional[str] = None,
        charset: typing.Optional[str],
        headers: typing.Optional[typing.List[EmailHeader]] = None,
        attachments: typing.Optional[typing.List[Path]] = None,
        write_eml_on_disk: bool = False,
    ):
        self.delegate = EmailMessage(Policies.get(policy))
        self.frm = frm
        self.to = to
        self.cc = cc or []
        self.bcc = bcc or []
        self.all_recipients = self.to + self.cc + self.bcc
        self.subject = subject
        self.headers = self._build_headers(headers or ())
        for header in self.headers:
            self.delegate[header.field_name] = header.value
        self.delegate.set_content(text, subtype="plain")
        self.html = html
        if html:
            self.delegate.add_alternative(self.html, subtype="html")
        self.attachments = attachments
        self.write_eml_on_disk = write_eml_on_disk

    def _build_headers(self, optional: typing.Sequence[EmailHeader]) -> typing.List[EmailHeader]:
        required = self._get_required_headers()
        required.extend(optional)
        return required

    def _get_required_headers(self) -> typing.List[EmailHeader]:
        return [
            EmailHeader(field, value)
            for field, value in [("From", self.frm), ("To", ", ".join(self.to)), ("Subject", self.subject)]
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


class EmailSender:
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
            result = smtp.send_message(self.message.delegate, self.message.frm, self.message.all_recipients)
            typer.secho(result, fg=typer.colors.GREEN, bold=True)
        return self.message


def email_factory(
    *,
    frm: str,
    to: typing.Union[typing.List[str], str],
    cc: typing.Optional[typing.List[str]] = None,
    bcc: typing.Optional[typing.List[str]] = None,
    subject: str = "",
    text: str = "",
    html: str = "",
    policy: str = "default",
    charset: typing.Optional[str] = None,
    headers: typing.Optional[typing.List[str]] = None,
    attachments: typing.Optional[typing.List[Path]] = None,
    write_eml_on_disk: bool = False,
) -> Email:
    """
    A simple factory, for Emails.
    """
    if headers is None:
        headers = []
    if isinstance(to, str):
        to = [to]
    resolved_headers = [EmailHeader.from_string(header) for header in headers]
    return Email(
        frm=frm,
        to=to,
        cc=cc,
        bcc=bcc,
        policy=policy,
        subject=subject,
        text=text,
        html=html,
        charset=charset,
        headers=resolved_headers,
        attachments=attachments,
        write_eml_on_disk=write_eml_on_disk,
    )
