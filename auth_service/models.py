from sqlalchemy.orm import DeclarativeBase,Mapped,mapped_column, relationship
from sqlalchemy import ForeignKey, DateTime
from datetime import datetime
from sqlalchemy import func

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__= "users_db"
    id:Mapped[int]=mapped_column(primary_key=True)
    user_name:Mapped[str]=mapped_column(nullable=False)
    email:Mapped[str]=mapped_column(nullable=False, unique=True)
    password_hash:Mapped[str]=mapped_column(nullable=False)
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(back_populates="user",cascade="all, delete-orphan")

class RefreshToken(Base):
    __tablename__ = "tokens_db"
    id:Mapped[int]=mapped_column(primary_key=True)
    user_id:Mapped[int]=mapped_column(ForeignKey('users_db.id'))
    token_hash:Mapped[str]= mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),server_default=func.now())
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),nullable=False)
    is_revoked: Mapped[bool] = mapped_column(default=False)
    user:Mapped["User"]=relationship(back_populates="refresh_tokens")