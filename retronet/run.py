import asyncio
import os
from hypercorn.config import Config
from hypercorn.asyncio import serve
# ? Find out where Claude got this from
from retroApp import create_asgi_app

async def main():
    config = Config()
    config.bind = ["0.0.0.0:65000"]
    config.workers = os.cpu_count()*2 + 1

    asgi_retroNet = create_asgi_app()
    await serve(asgi_retroNet, config)

if __name__ == "__main__":
    asyncio.run(main())