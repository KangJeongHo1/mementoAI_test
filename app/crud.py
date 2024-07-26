from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import delete
from . import models
from datetime import datetime
from typing import Optional

async def create_url(db: AsyncSession, url: str, short_url: str, expiration_date: Optional[datetime]):
    """
    데이터베이스에 새로운 URL 항목을 생성합니다.

    주어진 단축 URL과 긴 URL, 선택적인 만료 날짜를 사용하여 새로운 URL 항목을 생성합니다.
    만료 날짜가 제공된 경우, 타임존 정보를 제거하고 저장합니다.

    Args:
        db (AsyncSession): 데이터베이스 세션입니다.
        url (str): 긴 URL입니다.
        short_url (str): 단축된 URL입니다.
        expiration_date (Optional[datetime]): 선택적인 만료 날짜입니다.

    Returns:
        models.URL: 생성된 URL 객체입니다.
    """
    if expiration_date is not None:
        if expiration_date.tzinfo is not None:
            expiration_date = expiration_date.replace(tzinfo=None)
    
    db_url = models.URL(url=url, short_url=short_url, expiration_date=expiration_date)
    db.add(db_url)
    await db.commit()
    await db.refresh(db_url)
    return db_url


async def get_url_by_short_url(db: AsyncSession, short_url: str):
    """
    단축 URL을 기준으로 URL 항목을 조회합니다.

    제공된 단축 URL을 기준으로 데이터베이스에서 URL 항목을 조회합니다. 
    현재 시간이 만료 날짜보다 이전인 경우 URL을 반환합니다.

    Args:
        db (AsyncSession): 데이터베이스 세션입니다.
        short_url (str): 조회할 단축 URL입니다.

    Returns:
        Optional[models.URL]: URL이 존재하고 만료되지 않은 경우 URL 객체를 반환하고, 그렇지 않으면 None을 반환합니다.
    """
    stmt = select(models.URL).filter(models.URL.short_url == short_url)
    result = await db.execute(stmt)
    db_url = result.scalars().first()
    now = datetime.utcnow()
    if db_url and (db_url.expiration_date is None or db_url.expiration_date > now):
        return db_url
    return None


async def increment_view_count(db: AsyncSession, short_url: str):
    """
    URL 항목의 조회 수를 증가시킵니다.

    제공된 단축 URL을 기준으로 URL 항목을 조회하고, 조회 수를 증가시킵니다.
    조회 수가 None인 경우 0으로 초기화한 후 증가시킵니다.

    Args:
        db (AsyncSession): 데이터베이스 세션입니다.
        short_url (str): 조회 수를 증가시킬 단축 URL입니다.
    """
    stmt = select(models.URL).filter(models.URL.short_url == short_url)
    result = await db.execute(stmt)
    db_url = result.scalars().first()
    if db_url:
        if db_url.view_count is None:
            db_url.view_count = 0  # 조회 수가 None인 경우 0으로 초기화
        db_url.view_count += 1
        await db.commit()
        await db.refresh(db_url)


async def get_view_count(db: AsyncSession, short_url: str) -> Optional[int]:
    """
    URL 항목의 조회 수를 조회합니다.

    제공된 단축 URL을 기준으로 URL 항목의 조회 수를 반환합니다.

    Args:
        db (AsyncSession): 데이터베이스 세션입니다.
        short_url (str): 조회 수를 가져올 단축 URL입니다.

    Returns:
        Optional[int]: URL의 조회 수를 반환하고, URL이 존재하지 않으면 None을 반환합니다.
    """
    stmt = select(models.URL).filter(models.URL.short_url == short_url)
    result = await db.execute(stmt)
    db_url = result.scalars().first()
    if db_url:
        return db_url.view_count
    return None

async def delete_expired_urls(db: AsyncSession):
    """
    만료된 URL 항목을 삭제합니다.

    현재 시간보다 이전인 만료된 URL 항목을 데이터베이스에서 삭제합니다.

    Args:
        db (AsyncSession): 데이터베이스 세션입니다.
    """
    now = datetime.utcnow()  # 현재 UTC 시간 가져오기
    stmt = delete(models.URL).where(models.URL.expiration_date < now)  # 삭제 쿼리
    await db.execute(stmt)  # 쿼리 실행
    await db.commit()  # 트랜잭션 커밋
