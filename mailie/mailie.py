import typing

import typer

from ._email import Dispatcher
from ._email import EmailFactory

app = typer.Typer()


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
