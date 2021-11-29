import dataclasses


@dataclasses.dataclass(frozen=True, repr=True)
class Configuration:
    policy: str
