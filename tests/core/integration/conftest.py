import time

import pytest
from server import BackgroundSMTPServer


@pytest.fixture(scope="function")
def integration_mail_server(request):
    server = BackgroundSMTPServer()
    server.start()
    request.addfinalizer(server.close)
    time.sleep(3)  # Todo: Wait for server to be ready!
