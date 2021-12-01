import typing

import typer

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
# TODO: add versioning via --version and exit
# TODO: Improve --help via better docstrings
# TODO: Auto detect common mail providers such as gmail and assist with configurations?
# TODO: Attachments inline support and auto detect types of files at runtime
# TODO: Consider env variables for passwords; or a prompt via typeR
# TODO: Setup typeR friendly testing using the built in client for invocation


@app.command()
def mail(
    frm: str,
    to: typing.List[str],
    policy: str = typer.Option("default", case_sensitive=False),
    subject: str = "",
    message: str = "",
    hostname: str = "",
    port: int = 0,
) -> None:
    typer.secho("Mailie is generating a mail.", fg=typer.colors.GREEN, bold=True)
    email = EmailFactory.create(frm=frm, to=to, policy=policy, message=message, subject=subject)
    typer.secho("Sending mail...", fg=typer.colors.GREEN, bold=True)
    Dispatcher(message=email, host=hostname, port=port).send()


@app.command()
def turret() -> None:
    ...
