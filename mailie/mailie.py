import typing

import typer

from .__version__ import VERSION
from ._email import Dispatcher
from ._email import EmailFactory

app = typer.Typer()

# TODO: headers subcommand
# TODO: auth subcommand
# TODO: attachments subcommand

# TODO: support charsets
# TODO: support recipients from a file, based on a delimiter (later)
# TODO: add short hand flags like -f, -t etc
# TODO: support reply-to by default
# TODO: add --conversation for debugging smtp conversations
# TODO: smarter SSL/startTLS etc
# TODO: add a flag for --ssl with --cert too?
# TODO: Allow a debugger or less verbose functionality
# TODO: add versioning via --version and exit (Completed - Added via `mailie mail --version` [X]).
# TODO: Improve --help via better docstrings
# TODO: Auto detect common mail providers such as gmail and assist with configurations?
# TODO: Attachments inline support and auto detect types of files at runtime
# TODO: Consider env variables for passwords; or a prompt via typeR
# TODO: Setup typeR friendly testing using the built in client for invocation
# TODO: Consider allowing a config file on disk
# TODO: Better native support for --from, in python land its a pain; in cli land its not!
# TODO: Write logs to file if required?


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
    frm: str,
    to: typing.List[str],
    policy: str = typer.Option("default", case_sensitive=False, callback=validate_policy),
    subject: str = "",
    message: str = "",
    hostname: str = "",
    port: int = 0,
    version: typing.Optional[bool] = typer.Option(None, "--version", "-v", callback=version_callback, is_eager=True),
) -> None:
    typer.secho("Mailie is generating a mail.", fg=typer.colors.BRIGHT_GREEN, bold=True)
    email = EmailFactory.create(frm=frm, to=to, policy=policy, message=message, subject=subject)
    typer.secho("Sending mail...", fg=typer.colors.BRIGHT_GREEN, bold=True)
    Dispatcher(message=email, host=hostname, port=port).send()


@app.command()
def turret() -> None:
    ...
