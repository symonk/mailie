import pytest
from click.testing import Result
from typer.testing import CliRunner

from mailie.mailie import app


@pytest.fixture
def run_mailie():
    runner = CliRunner()

    def invoke(*args, **kwargs) -> Result:
        return runner.invoke(app, *args, **kwargs)

    return invoke
