from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from . import models
from datetime import datetime
from typing import Optional

async def create_url(db: AsyncSession, url: str, short_url: str, expiration_date: Optional[datetime]):
    if expiration_date is not None:
        if expiration_date.tzinfo is not None:
            expiration_date = expiration_date.replace(tzinfo=None)
    
    db_url = models.URL(url=url, short_url=short_url, expiration_date=expiration_date)
    db.add(db_url)
    await db.commit()
    await db.refresh(db_url)
    return db_url

async def get_url_by_short_url(db: AsyncSession, short_url: str):
    stmt = select(models.URL).filter(models.URL.short_url == short_url)
    result = await db.execute(stmt)
    db_url = result.scalars().first()
    now = datetime.utcnow()
    if db_url and (db_url.expiration_date is None or db_url.expiration_date > now):
        return db_url
    return None

async def increment_view_count(db: AsyncSession, short_url: str):
    stmt = select(models.URL).filter(models.URL.short_url == short_url)
    result = await db.execute(stmt)
    db_url = result.scalars().first()
    if db_url:
        if db_url.view_count is None:
            db_url.view_count = 0  # 초기값 설정
        db_url.view_count += 1
        await db.commit()
        await db.refresh(db_url)

async def get_view_count(db: AsyncSession, short_url: str) -> Optional[int]:
    stmt = select(models.URL).filter(models.URL.short_url == short_url)
    result = await db.execute(stmt)
    db_url = result.scalars().first()
    if db_url:
        return db_url.view_count
    return None

async def delete_expired_urls(db: AsyncSession):
    now = datetime.utcnow()
    stmt = select(models.URL).filter(models.URL.expiration_date < now)
    result = await db.execute(stmt)
    expired_urls = result.scalars().all()
    for url in expired_urls:
        await db.delete(url)
    await db.commit()
