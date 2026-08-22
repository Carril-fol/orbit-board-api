from datetime import datetime
from typing import AsyncGenerator
from enum import Enum

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from ..config.settings import settings    

connect_args = {
    "statement_cache_size": 0,
    "prepared_statement_cache_size": 0,
}

if settings.db_ssl:
    connect_args["ssl"] = True
 
engine = create_async_engine(
    settings.neon_database_url,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=5,
    max_overflow=10,
    connect_args=connect_args,
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