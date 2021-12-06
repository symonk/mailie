import typing

import typer

from .__version__ import VERSION
from ._email import email_factory
from ._utility import unpack_recipients_from_csv

app = typer.Typer(name="mail")


# TODO (General)
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


def validate_policy(ctx: typer.Context, value: str) -> typing.Optional[str]:
    if not ctx.resilient_parsing:
        supported = "default", "smtp", "smtputf8", "strict", "http"
        value = value.lower()
        if value not in supported:
            raise typer.BadParameter(f"--policy must be in: {supported}")
        return value
    return None


def unpack_recipients(ctx: typer.Context, recipients: typing.List[str]) -> typing.Optional[typing.List[str]]:
    """
    Validates the mail `--to` input, for any of the inputs, if they are a valid
    file on disk (csv) we will extract the email addresses from the file delimiting
    on `,`.  The emails are then squashed into a flat list and handed off to the
    `Email` instance.
    """
    if not ctx.resilient_parsing:
        return [
            email for group in [unpack_recipients_from_csv(recipient) for recipient in recipients] for email in group
        ]
    return None


@app.command()
def mail(
    frm: str = typer.Option(..., "--from", "-f"),
    to: typing.List[str] = typer.Option(
        ...,
        "--to",
        "-t",
        callback=unpack_recipients,
    ),
    cc: typing.List[str] = typer.Option(..., "--cc", callback=unpack_recipients),
    bcc: typing.List[str] = typer.Option(..., "--bcc", callback=unpack_recipients),
    policy: str = typer.Option("default", case_sensitive=False, callback=validate_policy),  # Todo: show_choices=?
    subject: str = typer.Option("", "--subject", "-sub", "-s"),
    message: str = typer.Option("", "--message", "-msg", "-m"),
    html: str = typer.Option("", "--html"),
    charset: str = typer.Option(None, "--charset", "-cs"),
    headers: typing.List[str] = typer.Option(None, "--headers", "-h"),
    verbosity: int = typer.Option(0, "-v", count=True),
) -> None:
    typer.secho(f"Mailie loaded.. (verbosity: {verbosity})", fg=typer.colors.BRIGHT_GREEN, bold=True)
    _ = email_factory(
        frm=frm,
        to=to,
        cc=cc,
        bcc=bcc,
        html=html,
        policy=policy,
        text_body=message,
        subject=subject,
        charset=charset,
        headers=headers,  # noqa
    )


@app.callback()
def main(version: bool = typer.Option(None, "--version", callback=version_callback, is_eager=True)):
    """
    A powerful python email command line tool.
    """
    if version:
        typer.secho(f"Mailie: {VERSION}", fg=typer.colors.BRIGHT_GREEN, bold=True)
        raise typer.Exit()
