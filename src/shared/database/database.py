from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from datetime import datetime
from typing import AsyncGenerator
from enum import Enum

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from ..config.settings import settings


def sanitize_url(url: str) -> str:
    """
    Converts 'sslmode' parameter to 'ssl' and removes incompatible parameters for asyncpg.
    """
    parsed = urlparse(url)
    if not parsed.query:
        return url

    query_params = parse_qs(parsed.query)

    if 'sslmode' in query_params:
        query_params['ssl'] = query_params.pop('sslmode')

    query_params.pop('channel_binding', None)

    new_query = urlencode(query_params, doseq=True)
    sanitized_parsed = parsed._replace(query=new_query)

    return urlunparse(sanitized_parsed)


engine = create_async_engine(
    sanitize_url(settings.neon_database_url),
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=5,
    max_overflow=10,
)


AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    
    def to_dict(self):
        data = {}

        for column in self.__table__.columns:
            value = getattr(self, column.name)

            if isinstance(value, datetime):
                value = value.isoformat()

            elif isinstance(value, Enum):
                value = value.value

            data[column.name] = value
            
        return data


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session