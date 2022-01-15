from __future__ import annotations

import logging
import typing
from email.errors import MessageDefect
from email.message import EmailMessage
from email.message import Message
from email.policy import SMTP as SMTP_DEFAULT_POLICY
from email.policy import Policy

from ._attachments import AllFilesStrategy
from ._attachments import Attachable
from ._attachments import FileAttachment  # noqa
from ._constants import FROM_HEADER
from ._constants import NON_MIME_AWARE_CLIENT_MESSAGE
from ._constants import SUBJECT_HEADER
from ._constants import TO_HEADER
from ._constants import UTF_8
from ._policy import policy_factory
from ._types import EMAIL_ATTACHMENT_PATH_ALIAS
from ._types import EMAIL_CHARSET_ALIAS
from ._types import EMAIL_HEADER_TYPE_ALIAS
from ._types import EMAIL_PARAM_TYPE_ALIAS
from ._types import EMAIL_PAYLOAD_ALIAS
from ._utility import emails_to_list
from ._utility import split_headers_per_rfc

log = logging.getLogger(__name__)

_T = typing.TypeVar("_T")


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

        :param policy: (Optional) An instance of `email.policy.Policy` used for governing disparate use cases. By
        default mailie will assume a `SMTP` policy that automatically handles /r/n.  In a nutshell; policies are used
        to customise the behaviour of various classes in pythons inbuilt email package.

        For more information see: https://docs.python.org/3/library/email.policy.html.  Below outlines some of
        the inbuilt policies available via python email:

            :: default (uses python line endings via /n - sometimes undesirable)
            :: SMTP (clone of default, with /r/n line endings for RFC compliance)
            :: SMTPUTF8 (a UTF-8 equivalent of `smtp`, useful for non-ASCII in sender/recipient data)
            :: HTTP (useful if serialising headers for HTTP traffic)
            :: strict (clone of default, except raise_on_defect is assigned `True` to prevent silent failures)

        If omitted by client code, mailie will assume a `SMTP` strict equivalent by default.  If this is undesirable
        pass your own policy, e.g email.policy.SMTP. For core policies; mailie supports passing a string to resolve
        the policy e.g `policy='SMTPUTF8'`.

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

        :param html: (Optional) A tuple of either length 1 or 2.  If the tuple is a single element
        then the value is considered the HTML content in it's unformatted, raw form.  An optional
        iterable of attachment paths can be provided; these will be have CID's generated implicitly
        and be formatted into the html content provided in the order in which they are provided.
        For that reason, a tuple is preferred; using a set cannot guarantee the CID for img src
        tags in the html template post-format processing.

        A string of html content to include in the payload (body) of the email.
        By default, html is omitted and a simple plain text mail is built, if provided the mail is
        converted to a multipart/alternative where the payload includes both plain text and HTML content.
        Depending on the recipient(s) client, displaying of this will vary however mailie will signal
        that the HTML is priority (by the order in which the data is transmitted).

        :param charset: (Optional) ...

        :param base_headers: (Optional) A list of strings which are RFC-5322 or RFC-6532 compliant, where the
        header field and the header value are separated by colon.

        :param attachments: (Optional) attachments path can support attaching files from the local
        file system to the email.  It can accept a single path (string or PathLike) or an iterable of
        paths (string or PathLike).  Additionally it can accept the path to a directory in which case
        all files located in that directory will be considered for attachments.  These attachments are
        NOT inline attachments; to provide inline attachments for the alternative body; pass a 2 length
        tuple to html=(..., ...).

        :param attachment_strategy: A class which implements the `mailie.Attachable` interface.  This class
        can be provided by the user at runtime in order implement a customised attachment lookup and attachment
        process.  If omitted mailie will use a basic file strategy that takes paths literally and creates
        `FileAttachment` objects out of them, if a directory is provided all files in that directory will be
        turned into `FileAttachments` and added to the email (NOT inline).  The default strategy does not
        recursive into sub directories to hunt for more files; implement your own strategy if that is what
        you desire.

        What kind of emails are typically sent and currently supported?
            :: Simple plaintext emails
            :: Simple alternative plaintext/html emails
            :: Html emails embedded/inline attachments
            :: Emails with normal attachments

        `Email` implements a the `Mapping` interface (partially) and is mostly concerned around `header`
        management in that regard.  Indexing of `Email` is based on it's headers.
    """

    def __init__(
        self,
        *,
        from_addr: str,
        to_addrs: typing.Union[typing.List[str], str],
        policy: typing.Union[str, Policy] = SMTP_DEFAULT_POLICY,
        cc: typing.Optional[typing.List[str]] = None,
        bcc: typing.Optional[typing.List[str]] = None,
        subject: str = "",
        text: str = "",
        html: typing.Optional[str] = None,
        charset: str = UTF_8,
        base_headers: typing.Optional[typing.List[str]] = None,
        attachments: typing.Optional[EMAIL_ATTACHMENT_PATH_ALIAS] = None,
        attachment_strategy: Attachable = AllFilesStrategy(),
        preamble: str = NON_MIME_AWARE_CLIENT_MESSAGE,
        epilogue: str = NON_MIME_AWARE_CLIENT_MESSAGE,
    ):
        self.delegate_message = EmailMessage(policy=policy_factory(policy))
        self.from_addr = from_addr
        self.to_addrs = emails_to_list(to_addrs)
        self.cc = emails_to_list(cc)
        self.bcc = emails_to_list(bcc)
        self.html = html
        self.text = text
        self.set_charset(charset)
        self.subject = subject
        self.preamble = preamble
        self.epilogue = epilogue
        self.attachments = attachment_strategy.generate(attachments)  # type: ignore [call-arg]

        # -- Delegation Specifics ---
        self.add_header(FROM_HEADER, self.from_addr)
        self.add_header(TO_HEADER, ", ".join(self.to_addrs))
        self.add_header(SUBJECT_HEADER, self.subject)

        for header in split_headers_per_rfc(base_headers):
            self.add_header(*header)

        # Text provided; set the text/plain content
        self.delegate_message.set_content(self.text, subtype="plain")

        if self.html:
            # multipart/alternative.
            # Todo: Handle content ids and inline attachments within this.
            self.delegate_message.add_alternative(self.html, subtype="html")

        # Handling normal non inline attachments
        # Todo: Async support required here likely.
        for attachment in self.attachments:
            self.add_attachment(attachment)

    def as_string(self, unixfrom: bool = False, maxheaderlen: int = 0, policy: typing.Optional[Policy] = None) -> str:
        """Return the entire email message flattened as a string.  If `unixfrom` is True, the envelope sender
        is included the string.  If maxheaderlen is `0`, the underlying policy is used for determining the
        max_line_length, an additional `policy=` can be passed to defer to that policy instead.
        """
        return self.delegate_message.as_string(unixfrom, maxheaderlen, policy)

    def __str__(self) -> str:
        """
        Returns the entire email message flattened as a string.
        """
        return self.as_string()

    def as_bytes(self, unixfrom: bool = False, policy: typing.Optional[Policy] = None) -> bytes:
        """
        Returns the entire email message flattened as a bytes object.  If `unixfrom` is True, the envelope
        sender is included in the bytes object.  `policy=` can be provided to override the default policy
        for various aspects of formatting.  Flattening the message may trigger changes to the underlying
        `EmailMessage` and this method may **not** be the best way to serialize the message.
        """
        return self.delegate_message.as_bytes(unixfrom, policy)

    def __bytes__(self) -> bytes:
        return self.as_bytes()

    def is_multipart(self) -> bool:
        """
        Return True if the message payload is a list of sub email messages.  If is_multipart() returns
        False the message Email payload should be a string which might be a `Content Transfer Encoding`
        binary object.
        """
        return self.delegate_message.is_multipart()

    def get_unixfrom(self) -> typing.Optional[str]:
        """
        Retrieve the `envelope sender` header.
        """
        return self.delegate_message.get_unixfrom()

    def set_unixfrom(self, unixfrom: str) -> Email:
        """
        Set the messages `envelope sender` header to `unixfrom`.  This is not a property just to keep
        API delegation with the underlying `EmailMessage`.
        """
        self.delegate_message.set_unixfrom(unixfrom)
        return self

    def __len__(self) -> int:
        """
        Return the total number of headers in the message, this tally includes duplicate headers.
        """
        return len(self.delegate_message)

    def __contains__(self, name: str) -> bool:
        """
        Check if a particular header is present in the email headers.  This check is case insensitive
        and name should omit the trailing colon `:`.
        """
        return name in self.delegate_message

    def __getitem__(self, name: str) -> typing.Any:
        """
        Ignoring case, retrieve the header with a field value of `name`.  If no header is found no `KeyError`
        is raised, but instead `None` is returned.  `name` does not include the trailing colon `:`.
        """
        return self.get(name)

    def __setitem__(self, name: str, value: typing.Any) -> None:
        """
        Adds a new header to the Email where name is the header field_name and value is the field_value
        respectively.  The header is appended to the messages existing headers.  This does **not**
        overwrite existing headers with the same name, but instead appends possible duplicates.  In
        order to perform an overwrite, consider calling `del` on the `Email` instance with the header
        field name, then appending this header.  `Email.replace_header(name, value)` can be used as
        a convenience method for replacing a single headers value.
        """
        self.delegate_message[name] = value

    def replace_header(self, _name: str, _value: typing.Any) -> Email:
        """
        Convenience method for overwriting an existing header with a new value.  This method will replace
        the first instance of the header with `_name`.  This method returns the Email instance for fluency.
        """
        self.delegate_message.replace_header(_name, _value)
        return self

    def __delitem__(self, name: str) -> typing.Any:
        """
        Deletes all headers of `name`.  If no headers are present this implicitly does nothing.
        """
        del self.delegate_message[name]

    def keys(self) -> typing.List[str]:
        """
        Return a list of all the messages header field names.
        """
        return self.delegate_message.keys()

    def values(self) -> typing.List[EMAIL_HEADER_TYPE_ALIAS]:
        """
        Return a list of all the messages header values.
        """
        return self.delegate_message.values()

    def items(self) -> typing.List[typing.Tuple[str, EMAIL_HEADER_TYPE_ALIAS]]:
        """
        Return a list of 2-tuples containing all the messages header field and head values respectively.
        """
        return self.delegate_message.items()

    def get(self, name: str, failobj: typing.Optional[_T] = None) -> _T:
        """
        Return the value of the header named `name`.  If the header is not present in the message
        then failobj is returned.  Invoked by `__getitem__`
        """
        return self.delegate_message.get(name, failobj)  # type: ignore [arg-type]

    def get_all(
        self, name: str, failobj: typing.Optional[_T] = None
    ) -> typing.Union[typing.List[EMAIL_HEADER_TYPE_ALIAS], _T]:
        """
        Return a list of the header values where `name` is the header name.  If there is no header with
        that name in the message, then `failobj` is returned.  If the header exists multiple times all
        of it's values are retruend.
        """
        return self.delegate_message.get_all(name, failobj)  # type: ignore [arg-type]

    def add_header(self, _name: str, _value: str, **_params: typing.Any) -> Email:
        self.delegate_message.add_header(_name, _value, **_params)
        return self

    def get_content_type(self) -> str:
        """
        Return the emails maintype/subtype.  If no `Content-Type` header exists in the email then
        `get_content_type()` is used to determine it.  If the `Content-Type` header is invalid,
        `plain/text` is returned.
        """
        return self.delegate_message.get_content_type()

    def get_content_maintype(self) -> str:
        """
        Return the maintype resolved via `get_content_type()` e.g `plain`
        """
        return self.delegate_message.get_content_maintype()

    def get_content_subtype(self) -> str:
        """
        Return the subtype resolved via `get_content_type()` e.g `text`
        """
        return self.delegate_message.get_content_subtype()

    def get_default_type(self) -> str:
        """
        Return the default content type.
        """
        return self.delegate_message.get_default_type()

    def set_default_type(self, ctype: str) -> Email:
        """
        Sets the default content type. Returns the `Email` instance for fluency
        """
        self.delegate_message.set_default_type(ctype)
        return self

    def get_params(self, failobj: _T, header: str, unquote: bool) -> typing.List[typing.Tuple[str, str]]:
        """
        Returns the messages content headers as a list of tuples split on the `=`.  In the
        cases where no `=` exists; an empty string is set.  Optional `failobj` is returned
        in the instance where there is no `Content-Type` header, header can be provided
        to change the search context from `Content-Type` to that particular header.
        """
        return self.delegate_message.get_params(failobj, header, unquote)

    def get_param(
        self, param: str, failobj: _T, header: str, unquote: bool
    ) -> typing.Union[_T, EMAIL_PARAM_TYPE_ALIAS]:
        return self.delegate_message.get_param(param, failobj, header, unquote)

    def del_param(self, param: str, header: str, requote: bool) -> Email:
        self.delegate_message.del_param(param, header, requote)
        return self

    def set_param(
        self,
        param: str,
        value: str,
        header: str = ...,
        requote: bool = ...,
        charset: typing.Optional[str] = None,
        language: str = ...,
        replace: bool = ...,
    ) -> None:
        self.delegate_message.set_param(param, value, header, requote, charset, language, replace)

    def set_type(self, type: str, header: str, requote: bool) -> Email:
        self.delegate_message.set_type(type, header, requote)
        return self

    def get_filename(self, failobj: _T = None) -> typing.Union[str, _T]:
        return self.delegate_message.get_filename(failobj)

    def get_boundary(self, failobj: _T = None) -> typing.Union[str, _T]:
        return self.delegate_message.get_boundary(failobj)

    def set_boundary(self, boundary: str) -> Email:
        self.delegate_message.set_boundary(boundary)
        return self

    def get_content_charset(self, failobj: _T) -> typing.Union[str, _T]:
        return self.delegate_message.get_content_charset(failobj)

    def get_charsets(self, failobj: _T) -> typing.Union[typing.Union[str], _T]:
        return self.delegate_message.get_charsets(failobj)

    def walk(self) -> typing.Generator[Email, None, None]:
        yield from self.delegate_message.walk()

    def get_content_disposition(self) -> typing.Optional[str]:
        return self.delegate_message.get_content_disposition()

    def get_body(self, preferencelist: typing.Sequence[str]) -> typing.Optional[EmailMessage]:
        return self.get_body(preferencelist)

    def iter_attachments(self) -> typing.Iterator[EmailMessage]:
        yield from self.delegate_message.iter_attachments()

    def clear(self) -> Email:
        """
        Clears the headers and payload from the delegated `EmailMessage` messaged.
        If you want to retain non Content- headers, use `clear_content()` instead.
        """
        self.delegate_message.clear()
        return self

    def clear_content(self) -> Email:
        """
        Clears the payload and all non Content- headers.
        """
        self.delegate_message.clear_content()
        return self

    def __bool__(self) -> bool:
        """
        If the `Email` has any defects returns `False`.
        """
        return not bool(self.defects)

    @property
    def defects(self) -> typing.List[MessageDefect]:
        return self.delegate_message.defects

    @property
    def smtp_recipients(self) -> typing.List[str]:
        return self.to_addrs + self.cc + self.bcc

    @property
    def smtp_arguments(self) -> typing.Tuple[EmailMessage, str, typing.List[str]]:
        return self.delegate_message, self.from_addr, self.smtp_recipients

    def attach(self, payload: Message) -> None:
        """
        Add the given payload to the current payload.

        The current payload will always be a list of objects after this method
        is called.  If you want to set the payload to a scalar object, use
        set_payload() instead.
        """
        self.delegate_message.attach(payload)

    def get_payload(self, i: typing.Optional[int] = None, decode: bool = False) -> typing.Optional[EMAIL_PAYLOAD_ALIAS]:
        return self.delegate_message.get_payload(i, decode)

    def set_payload(self, payload: EMAIL_PAYLOAD_ALIAS, charset: EMAIL_CHARSET_ALIAS) -> Email:
        self.delegate_message.set_payload(payload, charset)
        return self

    def set_charset(self, charset: EMAIL_CHARSET_ALIAS) -> Email:
        self.delegate_message.set_charset(charset)
        return self

    def get_charset(self) -> EMAIL_CHARSET_ALIAS:
        return self.delegate_message.get_charset()

    def tree_view(self, *, message: Message = None, file=None, level: int = 0) -> None:
        """
        Write the structure of this message to stdout. This is handled recursively.
        """
        message = message or self.delegate_message
        print(f"{'-' * level}{message.get_content_type()}")
        if message.is_multipart():
            for sub_part in message.get_payload():
                self.tree_view(message=sub_part, file=file, level=level + 1)

    def add_attachment(self, attachment: FileAttachment) -> Email:
        main, sub = attachment.mime_types
        self.delegate_message.add_attachment(attachment.data, maintype=main, subtype=sub, filename=attachment.name)
        return self

    async def async_add_attachment(self, attachment: FileAttachment) -> Email:
        ...
        return self

    def set_content(self, data: str, x: str) -> Email:
        self.delegate_message.set_content(data, x)
        return self

    def __iter__(self) -> typing.Iterator[str]:
        yield from self.delegate_message
