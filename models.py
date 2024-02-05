import os
from sqlalchemy import VARCHAR
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped

POSTGRES_USER = os.getenv('DB_USER', 'swapi')
POSTGRES_PASSWORD = os.getenv('DB_PASSWORD', 'secret')
POSTGRES_DB = os.getenv('DB_NAME', 'swapi')
POSTGRES_PORT = os.getenv('DB_PORT', '5431')
POSTGRES_HOST = os.getenv('DB_HOST', 'localhost')

PG_DSN = f'postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}'

engine = create_async_engine(PG_DSN)
Session = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase, AsyncAttrs):
    pass


class SwapiPeople(Base):
    __tablename__ = 'swapi_people'

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(VARCHAR(50))
    height: Mapped[str] = mapped_column(VARCHAR(20))
    mass: Mapped[str] = mapped_column(VARCHAR(20))
    hair_color: Mapped[str] = mapped_column(VARCHAR(20))
    skin_color: Mapped[str] = mapped_column(VARCHAR(20))
    eye_color: Mapped[str] = mapped_column(VARCHAR(20))
    birth_year: Mapped[str] = mapped_column(VARCHAR(20))
    gender: Mapped[str] = mapped_column(VARCHAR(20))
    homeworld: Mapped[str] = mapped_column(VARCHAR(100))
    films: Mapped[str] = mapped_column(VARCHAR(300))
    species: Mapped[str] = mapped_column(VARCHAR(300), nullable=True)
    starships: Mapped[str] = mapped_column(VARCHAR(300), nullable=True)
    vehicles: Mapped[str] = mapped_column(VARCHAR(300), nullable=True)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    await engine.dispose()
