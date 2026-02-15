from datetime import datetime, timedelta
from enum import Enum

from sqlalchemy import func, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, registry, relationship

table_registry = registry()


class SeatStatus(str, Enum):
    free = 'free'
    on_hold = 'on_hold'
    confirmed = 'confirmed'
    expired = 'expired'



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
        back_populates='owner',
        init=False,
        lazy='selectin',
    )

    created_sessions: Mapped[list[Session]] = relationship(
        back_populates='creator',
        init=False,
        lazy='selectin',
    )

    reserved_seats: Mapped[list[SeatReservation]] = relationship(
        back_populates='user',
        init=False,
        cascade='all, delete-orphan',
        lazy='selectin',
    )


@table_registry.mapped_as_dataclass()
class Movie:
    __tablename__ = 'movies'

    id: Mapped[str] = mapped_column(primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey('users.id'))

    title: Mapped[str] = mapped_column(unique=True, nullable=False)
    year: Mapped[int] = mapped_column(nullable=False)
    genre: Mapped[str] = mapped_column(nullable=False)
    poster_path: Mapped[str] = mapped_column(unique=True, nullable=False)
    poster_url: Mapped[str] = mapped_column(unique=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False, init=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now(), nullable=False, init=False
    )

    owner: Mapped[User] = relationship(
        back_populates='movies',
        init=False,
    )
    sessions: Mapped[list[Session]] = relationship(
        back_populates='movie',
        init=False,
        cascade='all, delete-orphan',
        lazy='selectin',
    )



@table_registry.mapped_as_dataclass()
class Session:
    __tablename__ = 'sessions'

    id: Mapped[str] = mapped_column(primary_key=True)
    movie_id: Mapped[str] = mapped_column(ForeignKey('movies.id'))
    user_id: Mapped[str] = mapped_column(ForeignKey('users.id'))
    cinema_room_id: Mapped[str] = mapped_column(ForeignKey('cinema_rooms.id'))

    session_time: Mapped[datetime] = mapped_column(nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False, init=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now(), nullable=False, init=False
    )

    movie: Mapped[Movie] = relationship(back_populates='sessions')
    cinema_room: Mapped[CinemaRoom] = relationship(back_populates='sessions')
    creator: Mapped[User] = relationship(back_populates='created_sessions')
    reservations: Mapped[list[SeatReservation]] = relationship(
        back_populates='session',
        cascade='all, delete-orphan',
    )


@table_registry.mapped_as_dataclass()
class CinemaRoom:
    __tablename__ = 'cinema_rooms'

    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    total_seats: Mapped[int] = mapped_column(nullable=False)

    seats: Mapped[list[Seat]] = relationship(
        back_populates='auditorium',
        cascade='all, delete-orphan',
    )

    sessions: Mapped[list['Session']] = relationship(
        back_populates='auditorium',
    )


@table_registry.mapped_as_dataclass()
class Seat:
    __tablename__ = 'seats'
    __table_args__ = (
        UniqueConstraint('cinema_room_id', 'row', 'column', name='uq_cinema_room_seat'),
    )

    id: Mapped[str] = mapped_column(primary_key=True)
    cinema_room_id: Mapped[str] = mapped_column(ForeignKey('cinema_rooms.id'))

    row: Mapped[str] = mapped_column(String(1), nullable=False)
    column: Mapped[int] = mapped_column(nullable=False)


    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False, init=False
    )
    cinema_room: Mapped[CinemaRoom] = relationship(back_populates='seats')
    reservations: Mapped[list[SeatReservation]] = relationship(back_populates='seat')

    is_aisle: Mapped[bool] = mapped_column(default=False, nullable=False)
    is_accessible: Mapped[bool] = mapped_column(default=False, nullable=False)



@table_registry.mapped_as_dataclass()
class SeatReservation:
    __tablename__ = 'seat_reservations'
    __table_args__ = (
        UniqueConstraint('session_id', 'seat_id', name='uq_session_seat_reservation'),
    )

    id: Mapped[str] = mapped_column(primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey('users.id'))
    session_id: Mapped[str] = mapped_column(ForeignKey('sessions.id'))
    seat_id: Mapped[str] = mapped_column(ForeignKey('seats.id'))

    status: Mapped[SeatStatus]
    expires_at: Mapped[datetime | None] = mapped_column(nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False, init=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now(), nullable=False, init=False
    )

    user: Mapped[User] = relationship(
        back_populates='seat_reservations',
        init=False,
    )

    session: Mapped[Session] = relationship(
        back_populates='seat_reservations',
        init=False,
    )

    seat: Mapped[Seat] = relationship(back_populates='seat_reservations')
