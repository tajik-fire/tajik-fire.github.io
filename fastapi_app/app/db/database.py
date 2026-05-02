import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    from app.data.seed_problems import seed_problems
    
    async with AsyncSessionLocal() as session:
        from sqlalchemy import select
        from app.models.models import Problem
        result = await session.execute(select(Problem).limit(1))
        problems = result.scalars().all()
        
        if len(problems) == 0:
            try:
                await seed_problems(session)
            except Exception as e:
                print(f"Error seeding problems: {e}")

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
