from sqlalchemy.orm import DeclarativeBase,Mapped,mapped_column

class Base(DeclarativeBase):
    pass

class Url(Base):
    __tablename__= "url_db"
    id:Mapped[int]=mapped_column(primary_key=True)
    owner_id:Mapped[int]=mapped_column(nullable=False)
    original_url:Mapped[str]
    shortcode:Mapped[str]=mapped_column(unique=True)