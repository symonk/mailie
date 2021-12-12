from __future__ import annotations

import typing
from email.iterators import _structure  # type: ignore [attr-defined]
from email.message import EmailMessage
from pathlib import Path

from ._header import FROM_HEADER
from ._header import SUBJECT_HEADER
from ._header import TO_HEADER
from ._policy import Policies
from ._types import EMAIL_HEADER_ALIAS
from ._utility import convert_strings_to_headers
from ._utility import emails_to_list


class Email:
    """
    An encapsulation and representation of an email message.  At present only simple plaintext
    mails and multipart/alternative plain + html content mails are supported.  Client code should
    opt for using the email_factory rather than importing and instantiating `Email` instances
    themselves.  Only keyword arguments are supported in both `Email` and `email_factory` in a bid
    to build a more robust API.

    An email message is a combination of RFC-2822 headers and a payload.  If the message is a container
    (e.g a multipart message) then the payload is a list of EmailMessage objects, otherwise it is just
    a string.

        :param from_addr: (Required) The envelope sender of the email.  This is what is provided during the SMTP
        communication as part of the `MAIL FROM` part of the conversation later.  Mailie will not assign a
        FROM header in the message itself, but consider this the envelope/unix from.

        :param to_addrs: (Required) The envelope recipient(s) of the email.  This is what is provided during the SMTP
        communication as part of the `RCPT TO` part of the conversation later.  to_addrs can be a single email address
        (str) or a list of email addresses.  In the event a single address is given, it will be converted to a list
        implicitly.

        :param policy: (Optional) ...

        :param cc: (Optional) A single email address (string) or an iterable of email addresses. In both cases the
        emails are converted to a list of distinct addresses.  Recipients set for cc (carbon copy) are all visible
        to each other; in order to include a hidden recipient, opt for `bcc=...` instead.  CC recipients are
        handled via a `CC` header and are also added to to_addrs and bcc during the SMTP conversation.

        Including arbitrary headers for CC is not advised as this is handled internally by the Email instance.

        :param bcc: (Optional) A single email address (string) or an iterable of email addresses. In both cases
        the emails are converted to a list of distinct addresses.  In older versions of python email handling
        via a BCC header revealed recipients, but is however fixed using send_message(...).  However mailie will
        not include a `BCC` header in the email regardless and all to_addrs; cc + bcc addresses will be compressed
        into a single iterable when having the SMTP conversation.

        Including arbitrary headers for BCC is not advised as this is handled internally by the Email instance.

        :param subject: (Optional) A string to include in the message as part of the subject header.
        By design emails do not REQUIRE a subject however it is good practice to include one.  If omitted
        the subject of the email will be empty ''.

        :param text: (Optional) A string of text to include as the text/plain payload (body) of the email.
        By default, an empty body will be created.  For simple plaintext mails, text= is the only data
        necessary, however for more multipart variants html & attachments  can be provided.

        :param html: (Optional) A string of html content to include in the payload (body) of the email.
        By default, html is omitted and a simple plain text mail is built, if provided the mail is
        converted to a multipart/alternative where the payload includes both plain text and HTML content.
        Depending on the recipient(s) client, displaying of this will vary however mailie will signal
        that the HTML is priority (by the order in which the data is transmitted).

        :param charset: (Optional) ...

        :param headers: (Optional) A list of either strings which are rfc-2822 compliant (name:value) or a
        list of `EmailHeader`.  In the event that strings are present in the iterable dataset, they are
        converted to `EmailHeader` instances internally.  All headers are then assigned onto the delegate
        EmailMessage prior to sending.

        :param attachments: (Optional) ...

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


        Dev priorities:
            :: Complete delegation
            :: Refactor API
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
        policy: str = "default",
        cc: typing.Optional[typing.List[str]] = None,
        bcc: typing.Optional[typing.List[str]] = None,
        subject: str = "",
        text: str = "",
        html: typing.Optional[str] = None,
        charset: str = "utf-8",
        headers: typing.Optional[EMAIL_HEADER_ALIAS] = None,
        attachments: typing.Optional[typing.List[Path]] = None,
        preamble: typing.Optional[str] = None,
        epilogue: typing.Optional[str] = None,
        hooks: typing.Optional[typing.Callable[[Email, typing.Dict[typing.Any, typing.Any]], None]] = None,
    ):
        self.delegate = EmailMessage(Policies.get(policy))
        self.from_addr = from_addr
        self.to_addrs = emails_to_list(to_addrs)
        self.cc = emails_to_list(cc)
        self.bcc = emails_to_list(bcc)
        self.html = html
        self.text = text
        self.charset = charset  # Todo: Where does this fit, charset of what exactly?
        # smtp servers do not care about email headers.
        self.subject = subject
        self.preamble = preamble  # Todo: Implement later
        self.epilogue = epilogue  # Todo: Implement later
        self.attachments = attachments  # Todo: Implement later
        self.hooks = hooks
        self.headers = convert_strings_to_headers(headers)

        # -- Delegation Specifics ---
        self.add_header(FROM_HEADER, self.from_addr)
        self.add_header(TO_HEADER, ", ".join(self.to_addrs))
        self.add_header(SUBJECT_HEADER, self.subject)

        # Text provided; set the text/plain content
        self.delegate.set_content(self.text, subtype="plain")
        if html:
            # html content provided; convert to multipart/alternative
            # Rendering is client specific here and mileage may vary on delivery.
            self.delegate.add_alternative(self.html, subtype="html")

        for header in self.headers:
            self.add_header(header.field_name, header.field_body)

    @property
    def smtp_recipients(self) -> typing.List[str]:
        return self.to_addrs + self.cc + self.bcc

    def smtp_arguments(self) -> typing.Tuple[EmailMessage, str, typing.List[str]]:
        return self.delegate, self.from_addr, self.smtp_recipients

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
