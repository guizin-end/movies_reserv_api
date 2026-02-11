from datetime import datetime

from sqlalchemy import func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, registry, relationship

table_registry = registry()


@table_registry.mapped_as_dataclass()
class User:
    __tablename__ = 'users'

    id: Mapped[str] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False, init=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now(), nullable=False, init=False
    )

    movies: Mapped[list[Movie]] = relationship(
        init=False,
        cascade='all, delete-orphan',
        lazy='selectin',
    )


@table_registry.mapped_as_dataclass()
class Movie:
    __tablename__ = 'movies'

    id: Mapped[str] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(unique=True, nullable=False)
    year: Mapped[int] = mapped_column(nullable=False)
    genre: Mapped[str] = mapped_column(nullable=False)
    poster_path: Mapped[str] = mapped_column(unique=True, nullable=False)
    poster_url: Mapped[str] = mapped_column(unique=True, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))

    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False, init=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now(), nullable=False, init=False
    )
