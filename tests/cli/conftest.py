import pytest
from click.testing import Result
from typer.testing import CliRunner

from mailie.mailie import app

runner = CliRunner()


@pytest.fixture
def run_mailie():
    def invoke(cmds, *args, **kwargs) -> Result:
        return runner.invoke(app, cmds, *args, **kwargs)

    return invoke
