import dataclasses

from ._types import EMAIL_PROVIDER_TYPES


@dataclasses.dataclass(frozen=True)
class Providers:
    """Simple tuples of well known providers"""

    LOCAL: EMAIL_PROVIDER_TYPES = ("localhost", 25)
    GMAIL: EMAIL_PROVIDER_TYPES = ("smtp.gmail.com", 465)
