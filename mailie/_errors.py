import dataclasses


@dataclasses.dataclass(frozen=True)
class SmtpError:
    """
    An encapsulation of an SMTP error message, includes both the error code and message.
    """

    code: int
    message: str
