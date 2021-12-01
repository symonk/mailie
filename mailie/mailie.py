import typer

app = typer.Typer()


@app.command()
def mail() -> None:
    typer.echo("Mailie is sending a mail...")


@app.command()
def turret() -> None:
    typer.echo("Mailis is turreting mails...")
