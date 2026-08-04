import asyncio

from src.ServerNetwork.AsyncClient import AsyncClient
from src.view.UserView import UserView


async def start_client():
    client = AsyncClient(host="127.0.0.1", port=65432)
    user_view = UserView(client=client)
    await user_view.run()


try:
    asyncio.run(start_client())
except KeyboardInterrupt:
    print("Client stopped.")  # noqa: T201
