from sqlalchemy import URL
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine

from src.infrastructure.storage.postgresql.config import DBConfig


def make_url(config: DBConfig):
    return URL(
        drivername="postgresql+asyncpg",
        username=config.user,
        password=config.password,
        host=config.host,
        port=int(config.port),
        database=config.name,
        query={}
    )


def async_engine(config: DBConfig) -> AsyncEngine:
    engine = create_async_engine(
        make_url(config),
        pool_size=150,
        max_overflow=50,
        pool_recycle=1800,
        pool_pre_ping=True,
        pool_use_lifo=False,
        connect_args={
            "timeout": 3600
        }
    )
    return engine

def get_sessionmaker(config: DBConfig) -> async_sessionmaker:
    engine = async_engine(config)
    return async_sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
        expire_on_commit=False
    )


DBSession = get_sessionmaker(DBConfig())
