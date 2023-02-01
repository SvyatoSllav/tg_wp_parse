import logging

from pydantic import PostgresDsn
from sqlalchemy.sql import text
from sqlalchemy.exc import ResourceClosedError
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession
from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed

from app.core.config import settings
from app.db.session import async_session_factory

logger = logging.getLogger(__name__)

max_tries = 60 * 5  # 5 minutes
wait_seconds = 1


@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
async def check_db_ready() -> None:
    try:
        db = async_session_factory()
        await db.execute("SELECT 1")
    except Exception as e:
        logger.error(e)
        raise e


async def create_db_if_needed() -> None:
    url = PostgresDsn.build(
        scheme="postgresql+asyncpg",
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        host=settings.POSTGRES_SERVER,
        path='/postgres',
    )
    engine = create_async_engine(url)
    if not await _database_exists(engine, settings.POSTGRES_DB):
        engine = create_async_engine(url, isolation_level="AUTOCOMMIT")
        await _create_database(engine, settings.POSTGRES_DB)


async def _database_exists(engine: AsyncEngine, database_name: str) -> bool:
    conn: AsyncSession
    async with engine.connect() as conn:
        logger.info("Checking if database exists")
        sql = text("SELECT 1 FROM pg_database WHERE datname='%s'" % database_name)
        res = await conn.scalar(sql)
        return bool(res)


async def _create_database(engine: AsyncEngine, database_name: str) -> None:
    conn: AsyncSession
    async with engine.connect() as conn:
        logger.info("Database doesnt exist, creating one...")
        sql = text("CREATE DATABASE %s" % database_name)
        try:
            await conn.scalar(sql)
        except ResourceClosedError:
            pass
        finally:
            logger.info("Database created")
