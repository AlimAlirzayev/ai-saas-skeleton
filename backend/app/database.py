from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.engine import URL
from .config import settings

connection_url = URL.create(
    drivername="postgresql+asyncpg",
    username=settings.postgres_user,
    password=settings.postgres_password,
    host="postgres",
    port=5432,
    database=settings.postgres_db,
)

engine = create_async_engine(
    connection_url,
    echo=False,
    connect_args={"ssl": False}
)

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
