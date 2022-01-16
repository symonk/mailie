import typing

PROVIDERS = {"LOCAL": ("localhost", 25), "GMAIL": ("smtp.gmail.com", 465)}


def provider_factory(provider: str = "local") -> typing.Tuple[str, int]:
    return PROVIDERS[provider.upper()]
