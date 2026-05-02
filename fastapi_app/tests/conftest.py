import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.db.database import Base
from app.core.config import settings


from app.models.models import (
    User, Chat, ChatMember, Message, Task,
    Problem, ProblemTranslation, TestCase, Submission,
    ProblemSolve, Contest, ContestProblem, ContestParticipation,
    Rating, Friendship, Notification, BlockedUser,
    LearningModule, LearningProblem, LearningEnrollment,
    SubmissionFeed, News, EmailCode, LoginAttempt, AuthToken, TempUser
)

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def test_engine():
    return create_async_engine(TEST_DATABASE_URL, echo=False)


@pytest.fixture(scope="function", autouse=True)
async def setup_database(test_engine):
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def test_db(test_engine):
    
    async_session = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        yield session


@pytest.fixture(scope="function")
async def client(test_db):
    from main import app
    
    async def override_get_db():
        yield test_db
    
    app.dependency_overrides = {
        "get_db": override_get_db
    }
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides = {}
