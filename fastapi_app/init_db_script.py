import asyncio
import os
os.chdir('/workspace/fastapi_app')

from app.db.database import engine, Base

async def create():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Check if tables were created
    from sqlalchemy import text
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        tables = result.fetchall()
        print(f"Tables created: {[t[0] for t in tables]}")

asyncio.run(create())
