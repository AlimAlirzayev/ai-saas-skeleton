from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from .config import settings

DATABASE_URL = (
    f"postgresql+asyncpg://{settings.postgres_user}:"
    f"{settings.postgres_password}@postgres:5432/"
    f"{settings.postgres_db}"
)

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"ssl": False}  # ← BU ƏLAVƏ OLUNDU
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