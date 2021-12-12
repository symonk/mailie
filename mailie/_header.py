from __future__ import annotations

FROM_HEADER = "From"
SUBJECT_HEADER = "Subject"
TO_HEADER = "To"


class EmailHeader:
    RFC_2822_DELIMITER = ":"

    """
    Representation of a RCF-2822 Header field.  An email header consists of a header
    field, followed by a colon and finally the field body which is then terminated
    by a carriage return and line feed (CRLF).  Characters in the field name must
    be composed of only US-ASCII characters (code points between 33 & 126).  Colon
    is not included as part of these code point limitations.  Header folding is
    a concept and when used can allow CRLF characters inside the field body.

        :: reference: https://datatracker.ietf.org/doc/html/rfc2822#section-2.2
    """

    def __init__(self, field_name: str, value: str):
        self.field_name = field_name
        self.field_body = value

    def __iter__(self):
        return iter((self.field_name, self.field_body))

    def __repr__(self) -> str:
        return f"Header=(field_name={self.field_name}, value={self.field_body})"

    @classmethod
    def from_string(cls, header: str) -> EmailHeader:
        return cls(*header.split(cls.RFC_2822_DELIMITER))
