import asyncore

import pytest
from server import FakeSMTPServer


@pytest.fixture(scope="session")
def mail_to_disk_server():
    server = FakeSMTPServer(("localhost", 1250), None)
    asyncore.loop()
    yield server
    server.close()
