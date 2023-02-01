import asyncio
import logging
from app.scripts.db import check_db_ready

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main() -> None:
    logger.info("Initializing service")
    await check_db_ready()
    logger.info("Service finished initializing")


if __name__ == "__main__":
    asyncio.run(main())
