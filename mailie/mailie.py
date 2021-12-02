import typing

import typer

from .__version__ import VERSION
from ._email import email_factory
from .commands import attach
from .commands import headers
from .commands import send

app = typer.Typer(name="mail")
app.add_typer(headers.app, name="headers")
app.add_typer(attach.app, name="attach")
app.add_typer(send.app, name="send")


# TODO (General)
# TODO: Add a `--version` flag on the root `mailie`?
# TODO: Allow general debugging and verbosity counts?
# TODO: Well documented --help for every argument & option?
# TODO: Expose environment variables for things like smtp passwords?
# TODO: Setup testing using the app runner for invocations of the CLI app?
# TODO: Consider adding a config file on disk? (maybe smtp data for 'known servers' to start?
# TODO: Add the capability to store the aforementioned debugging to a file on disk?
# TODO: Build a robust read me and sphinx/makedocs documentation website?
# TODO: Consider async send capabilities
# TODO: Consider a turret capability when async is in play

# -----

# TODO (Send)
# TODO: Support --ssl, --starttls etc?
# TODO: Add support for a --cert if using ssl etc?
# TODO: Add debugging information around SMTP conversations?
# TODO: Add common configuration for known providers like gmail?

# -----

# TODO (Mail)
# TODO: Add support for charsets?
# TODO: Support recipients from a file with a delimiter?
# TODO: Add shorthand flags for most options (-f, -t etc)?
# TODO: Support --reply-to & -rt explicitly?
# TODO: Better support for --from, CLI is fine but it is a python keyword?

# -----

# TODO (Attach)
# TODO: Support attachments; inline?
# TODO: Auto detect attachment mime types?


def version_callback(value: bool):
    if value:
        typer.secho(f"Mailie version: {VERSION}", fg=typer.colors.BRIGHT_GREEN, bold=True)
        raise typer.Exit()


def validate_policy(value: str) -> str:
    supported = "default", "smtp", "smtputf8", "strict", "http"
    value = value.lower()
    if value not in supported:
        raise typer.BadParameter(f"--policy must be in: {supported}")
    return value


@app.command()
def mail(
    frm: str = typer.Option(..., "--from", "-f"),
    to: typing.List[str] = typer.Option(..., "--to", "-t"),
    policy: str = typer.Option("default", case_sensitive=False, callback=validate_policy),
    subject: str = "",
    message: str = "",
) -> None:
    typer.secho("Mailie is generating a mail.", fg=typer.colors.BRIGHT_GREEN, bold=True)
    _ = email_factory(frm=frm, to=to, policy=policy, message=message, subject=subject)


@app.callback()
def main(version: bool = False):
    ...
