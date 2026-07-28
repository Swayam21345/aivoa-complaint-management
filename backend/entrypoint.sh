#!/bin/bash
set -e

echo "[AICCMS Backend] Waiting for database connection..."
python -c "
import time, asyncio, sys
from sqlalchemy.ext.asyncio import create_async_engine
from app.config import get_settings

async def check_db():
    settings = get_settings()
    engine = create_async_engine(settings.database_url)
    for i in range(30):
        try:
            async with engine.connect() as conn:
                print('[AICCMS Backend] Database connection successful!')
                return
        except Exception as e:
            print(f'[AICCMS Backend] Waiting for database... retry {i+1}/30 ({e})')
            await asyncio.sleep(2)
    print('[AICCMS Backend] Failed to connect to database within timeout.')
    sys.exit(1)

asyncio.run(check_db())
"

echo "[AICCMS Backend] Running Alembic database migrations..."
alembic upgrade head

echo "[AICCMS Backend] Starting Uvicorn ASGI application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
