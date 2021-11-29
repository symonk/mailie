import subprocess

import pytest


@pytest.fixture
def null_smtp_server():
    proc = subprocess.Popen(["python", "-m", "smtpd", "-n", "-c", "DebuggingServer", "localhost:2500"])
    yield proc
    proc.kill()
