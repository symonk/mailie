import typer

from ._email import Dispatcher
from ._email import EmailFactory

app = typer.Typer()


@app.command()
def mail(
    frm: str,
    to: str,
    policy: str = typer.Option("default", case_sensitive=False),
    subject: str = "",
    hostname: str = "",
    port: int = 0,
) -> None:
    typer.secho("Mailie is generating a mail.", fg=typer.colors.GREEN, bold=True)
    with typer.progressbar(range(50)):
        email = EmailFactory.create(frm=frm, to=to, policy=policy, subject=subject)
        typer.secho("Sending mail...", fg=typer.colors.GREEN, bold=True)
        Dispatcher(message=email, host=hostname, port=port).send()


@app.command()
def turret() -> None:
    ...
