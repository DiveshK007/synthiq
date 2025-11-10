"""
Database models and setup for orchestrator service
"""
import os
from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field, create_engine, Session, select
from sqlalchemy import JSON, Column

# Database URL from environment or default to SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./synthiq.db")

# Create engine
engine = create_engine(DATABASE_URL, echo=False)


class Job(SQLModel, table=True):
    """Job model for database storage"""
    id: str = Field(primary_key=True)
    status: str = Field(index=True)  # queued, running, done, error
    error: Optional[str] = None
    progress: dict = Field(sa_column=Column(JSON), default_factory=dict)
    result: Optional[dict] = Field(sa_column=Column(JSON), default=None)
    created_at: int = Field(index=True)
    updated_at: int
    user_id: Optional[str] = Field(default=None, index=True)
    sources: dict = Field(sa_column=Column(JSON), default_factory=dict)
    goal: str = ""


def init_db():
    """Initialize database tables"""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Get database session"""
    return Session(engine)


def create_job(job_id: str, sources: list, goal: str, user_id: Optional[str] = None) -> Job:
    """Create a new job in database"""
    now = int(datetime.utcnow().timestamp() * 1000)
    job = Job(
        id=job_id,
        status="queued",
        error=None,
        progress={"ingest": 0, "summarize": 0, "viz": 0},
        result=None,
        created_at=now,
        updated_at=now,
        user_id=user_id,
        sources={"sources": sources},
        goal=goal
    )
    with get_session() as session:
        session.add(job)
        session.commit()
        session.refresh(job)
    return job


def get_job(job_id: str) -> Optional[Job]:
    """Get job from database"""
    with get_session() as session:
        statement = select(Job).where(Job.id == job_id)
        return session.exec(statement).first()


def update_job(job_id: str, **updates) -> Optional[Job]:
    """Update job in database"""
    with get_session() as session:
        statement = select(Job).where(Job.id == job_id)
        job = session.exec(statement).first()
        if not job:
            return None
        
        for key, value in updates.items():
            setattr(job, key, value)
        
        job.updated_at = int(datetime.utcnow().timestamp() * 1000)
        session.add(job)
        session.commit()
        session.refresh(job)
        return job


def list_jobs(user_id: Optional[str] = None, limit: int = 100, offset: int = 0) -> list[Job]:
    """List jobs from database"""
    with get_session() as session:
        statement = select(Job)
        if user_id:
            statement = statement.where(Job.user_id == user_id)
        statement = statement.order_by(Job.created_at.desc()).limit(limit).offset(offset)
        return list(session.exec(statement).all())

