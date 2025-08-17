"""
Pytest configuration and fixtures for the test suite.
"""

import sys
import os

# Add the server directory to Python path for module imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from models.base import Base
from routers import user_router
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


@pytest.fixture
def db_engine():
    """Create a test database engine using SQLite in memory with thread safety."""
    engine = create_engine(
        "sqlite:///:memory:",
        echo=False,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    # Enable foreign key constraints for SQLite
    from sqlalchemy import event
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
    
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def db_session(db_engine):
    """Create a database session for testing."""
    SessionLocal = sessionmaker(bind=db_engine)
    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def test_app(db_session):
    """Create a test FastAPI app with database dependency override."""
    app = FastAPI(title="Test App")

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    # Import and override the dependency
    from database import get_mysql_db

    app.dependency_overrides[get_mysql_db] = override_get_db

    # Add routers
    from fastapi import APIRouter

    api_router = APIRouter(prefix="/api")
    api_router.include_router(user_router)
    app.include_router(api_router)

    return app


@pytest.fixture
def client(test_app):
    """Create a test client."""
    with TestClient(test_app) as test_client:
        yield test_client
