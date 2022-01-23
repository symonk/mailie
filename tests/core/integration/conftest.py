import time

import pytest
from server import BackgroundSMTPServer


@pytest.fixture(scope="function")
def mail_to_disk_server(request, tmpdir):
    server = BackgroundSMTPServer()
    server.start()
    request.addfinalizer(server.close)
    time.sleep(1.5)  # Todo: Wait for server to be ready!
