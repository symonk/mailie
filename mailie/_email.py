from __future__ import annotations

import email.policy
import smtplib
import typing
from email.message import EmailMessage


class Email:
    # version 0.1.0 will encompass a simple plaintext mail; then iterate.
    def __init__(
        self,
        *,
        policy: email.policy.EmailPolicy = email.policy.SMTP,
        subject: str = "",
        frm: str = "",
        to: str = "",
    ):
        self.message = EmailMessage(policy)
        self.add_header("Subject", subject)
        self.add_header("From", frm)
        self.add_header("To", to)

    def __str__(self) -> str:
        return str(self.message)

    def __bytes__(self) -> bytes:
        return bytes(self.message)

    def add_header(self, name: str, value: typing.Any, **params) -> Email:
        self.message.add_header(name, value, **params)
        return self

    def get_content_type(self) -> str:
        return self.message.get_content_type()

    def set_payload(self, payload: str, charset=None) -> Email:
        self.message.set_payload(payload, charset)
        return self

    def send(self) -> Email:
        smtpobj = smtplib.SMTP("localhost", port=2500)
        smtpobj.sendmail(self.message["From"], [self.message["To"]], str(self))
        return self
