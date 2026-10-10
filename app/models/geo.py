from typing import List, Optional
from sqlalchemy import BigInteger, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Country(Base):
    __tablename__ = "countries"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)

    states: Mapped[List["State"]] = relationship("State", back_populates="country", cascade="all, delete-orphan")


class State(Base):
    __tablename__ = "states"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    country_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("countries.id", ondelete="CASCADE"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    country: Mapped["Country"] = relationship("Country", back_populates="states")
    cities: Mapped[List["City"]] = relationship("City", back_populates="state", cascade="all, delete-orphan")


class City(Base):
    __tablename__ = "cities"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    state_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("states.id", ondelete="CASCADE"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    state: Mapped["State"] = relationship("State", back_populates="cities")
