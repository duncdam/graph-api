import os
import logging
import asyncpg
from typing import Optional
from contextlib import asynccontextmanager

from app.utils import enums

logger = logging.getLogger(__name__)


class DatabaseManager:
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None

    async def connect(self):
        """Create database connection pool"""
        if not self.pool:
            self.pool = await asyncpg.create_pool(
                host=enums.postgres.host,
                port=enums.postgres.port,
                database=enums.postgres.database,
                user=enums.postgres.user or os.getenv("DB_USER", "graph"),
                password=enums.postgres.password,
                min_size=1,
                max_size=10,
                command_timeout=60,
            )

    async def disconnect(self):
        """Close database connection pool"""
        if self.pool:
            await self.pool.close()
            self.pool = None

    @asynccontextmanager
    async def get_connection(self):
        """Get database connection from pool"""
        if not self.pool:
            await self.connect()

        async with self.pool.acquire() as connection:
            yield connection


# Global database manager instance
db_manager = DatabaseManager()


async def get_db_connection():
    """Dependency to get database connection"""
    async with db_manager.get_connection() as connection:
        yield connection
