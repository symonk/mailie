import pytest

from mailie import AsyncClient


@pytest.mark.skip
@pytest.mark.asyncio
async def test_async_client(mail_to_disk_server):
    async with AsyncClient(port=9222) as client:
        await client.send(email=mail_to_disk_server, port=9222)
