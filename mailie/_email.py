from __future__ import annotations

import smtplib
import typing
from email.iterators import _structure  # type: ignore [attr-defined]
from email.message import EmailMessage
from pathlib import Path

import typer

from ._policy import Policies


class Email:
    # version 0.1.0 will encompass a simple plaintext mail; then iterate.
    def __init__(
        self,
        *,
        frm: str,
        to: typing.List[str],
        policy: str,
        subject: str = "",
        text_body: str = "",
        html: typing.Optional[str] = None,
        charset: typing.Optional[str],
        headers: typing.Optional[typing.Sequence[EmailHeader]] = None,
        attachments: typing.Optional[typing.Sequence[Path]] = None,
        write_eml_on_disk: bool = False,
    ):
        self.frm = frm
        self.to = ", ".join(to)
        self.subject = subject
        self.delegate = EmailMessage(Policies.get(policy))
        self.headers = self._build_headers(headers or ())
        self.delegate.set_content(text_body, subtype="plain")
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
            for field, value in [("From", self.frm), ("To", self.to), ("Subject", self.subject)]
        ]

    def render(self) -> None:
        # TODO: Implement better handling here; return a dictionary of parent:root nodes?
        _structure(self.delegate)

    def __str__(self) -> str:
        return str(self.delegate)

    def __bytes__(self) -> bytes:
        return bytes(self.delegate)

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


class Dispatcher:
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
        with smtplib.SMTP(self.host, port=self.port) as smtp:
            result = smtp.sendmail(self.message.delegate["From"], [self.message.delegate["To"]], str(self.message))
            typer.secho(result, fg=typer.colors.GREEN, bold=True)
        return self.message


def email_factory(
    *,
    frm: str,
    to: typing.Union[typing.List[str], str],
    subject: str = "",
    text_body: str = "",
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
    resolved_headers = [EmailHeader.from_string(header) for header in headers]
    return Email(
        frm=frm,
        to=[to] if isinstance(to, str) else to,
        policy=policy,
        subject=subject,
        text_body=text_body,
        html=html,
        charset=charset,
        headers=resolved_headers,
        attachments=attachments,
        write_eml_on_disk=write_eml_on_disk,
    )
