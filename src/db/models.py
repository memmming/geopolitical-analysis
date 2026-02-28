"""
Database Models and ORM Configuration
"""
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Float,
    JSON,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from pathlib import Path

from src.config import DATABASE_PATH

# Ensure data directory exists
DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

# Create database engine
engine = create_engine(f"sqlite:///{DATABASE_PATH}", echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class Article(Base):
    """
    Article model for storing RSS articles
    """
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(500), nullable=False)
    url = Column(String(1000), unique=True, nullable=False, index=True)
    pub_date = Column(DateTime, nullable=True, index=True)
    content = Column(Text, nullable=True)
    source_domain = Column(String(200), nullable=True)
    source_name = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationship with analysis
    analysis = relationship("Analysis", back_populates="article", uselist=False)

    def __repr__(self):
        return f"<Article(id={self.id}, title='{self.title[:30]}...', url='{self.url[:40]}...')>"


class Analysis(Base):
    """
    Analysis model for storing AI-generated analysis
    """
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=False, unique=True)
    summary = Column(Text, nullable=True)
    category = Column(String(50), nullable=True)
    tags = Column(JSON, nullable=True)  # Store as JSON array
    score = Column(Integer, nullable=True)
    deep_insight = Column(Text, nullable=True)
    impact_level = Column(String(50), nullable=True)
    status = Column(String(50), default="进行中", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationship with article
    article = relationship("Article", back_populates="analysis")

    # Categories enum validation
    VALID_CATEGORIES = [
        "Conflict & Security",
        "Diplomacy & Policy",
        "Global Economy & Trade",
        "Energy & Resources",
        "Tech War & Cyber",
        "Elections & Politics",
    ]

    # Impact levels enum validation
    VALID_IMPACT_LEVELS = ["Global Shift", "High Risk", "Moderate", "Low"]

    def __repr__(self):
        return f"<Analysis(id={self.id}, article_id={self.article_id}, score={self.score}, status='{self.status}')>"


class Report(Base):
    """
    Report model for caching generated daily reports
    """
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    report_date = Column(String(10), unique=True, nullable=False, index=True)  # Format: YYYY-MM-DD
    markdown_content = Column(Text, nullable=True)
    chart_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Report(id={self.id}, date='{self.report_date}', created_at='{self.created_at}')>"


def init_db():
    """Initialize the database and create all tables"""
    Base.metadata.create_all(bind=engine)
    print(f"Database initialized at: {DATABASE_PATH}")


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


if __name__ == "__main__":
    # Initialize database
    init_db()
    print("Database tables created successfully")
