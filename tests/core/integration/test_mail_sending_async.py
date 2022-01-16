import pytest

from mailie import AsyncClient


@pytest.mark.asyncio
def test_async_client(mail_to_disk_server):
    async with AsyncClient(port=9222) as client:
        await client.send(email=mail_to_disk_server)