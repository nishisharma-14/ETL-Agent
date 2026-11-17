from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from src.config import settings

Base = declarative_base()

class ProductModel(Base):
    """
    SQL Model representing the products table.
    Stores clean, normalized data extracted from the external API.
    """
    __tablename__ = "products"

    product_id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False, index=True)
    price = Column(Float, nullable=False)
    rating = Column(Float, nullable=False, default=0.0)
    stock = Column(Integer, nullable=False, default=0)
    brand = Column(String(100), nullable=True)
    updated_at = Column(String(50), nullable=False)

# Initialize SQLAlchemy engine & session maker
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db() -> None:
    """Create all database tables if they do not exist."""
    Base.metadata.create_all(bind=engine)
