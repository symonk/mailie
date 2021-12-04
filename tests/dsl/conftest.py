import pytest


@pytest.fixture()
def render_checker():
    def parse(output: str):
        """
        # TODO: Consider this as part of the mail API, render(...) could do exactly this but programmatically
        # TODO: W/o leaving us parsing stdout?
        Splits the output of the email _structure(...).  Handled via tabbing
        """
        return list(map(str.strip, output.splitlines()))

    return parse
