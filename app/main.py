from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from . import crud, models, schemas
from .database import get_db, engine
from .utils import generate_short_url
from fastapi.responses import RedirectResponse

app = FastAPI(
    title="My URL Shortener API",
    description="API to shorten URLs and manage redirections",
    version="1.0.0",
    docs_url="/swagger",
    redoc_url="/redoc"
)

@app.on_event("startup")
async def startup_event():
    """
    애플리케이션 시작 시 호출되는 이벤트 핸들러입니다.

    데이터베이스의 테이블을 생성하고, 만료된 URL을 삭제하는 백그라운드 작업을 수행합니다.
    """
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    # 백그라운드 작업으로 만료된 URL 삭제
    async with engine.connect() as conn:
        await crud.delete_expired_urls(conn)

@app.post("/shorten", response_model=schemas.URL)
async def create_short_url(url: schemas.URLCreate, db: AsyncSession = Depends(get_db)):
    """
    긴 URL을 단축 URL로 변환하여 데이터베이스에 저장합니다.

    요청 본문에서 긴 URL과 만료 날짜를 받아 단축 URL을 생성하고, 이를 데이터베이스에 저장합니다.
    단축 URL이 중복되지 않도록 확인한 후 저장합니다.

    Args:
        url (schemas.URLCreate): 생성할 URL의 정보입니다.
        db (AsyncSession): 데이터베이스 세션입니다.

    Returns:
        schemas.URL: 생성된 URL의 정보입니다.
    """
    short_url = generate_short_url()
    while await crud.get_url_by_short_url(db, short_url):
        short_url = generate_short_url()
    db_url = await crud.create_url(db, url.url, short_url, url.expiration_date)
    return db_url

@app.get("/{short_url}", response_class=RedirectResponse)
async def redirect_to_original_url(short_url: str, db: AsyncSession = Depends(get_db)):
    """
    단축 URL을 원래의 긴 URL로 리디렉션합니다.

    요청된 단축 URL을 데이터베이스에서 조회하여, 해당 URL로 리디렉션합니다.
    이 과정에서 URL의 조회 수를 증가시킵니다.

    Args:
        short_url (str): 단축된 URL입니다.
        db (AsyncSession): 데이터베이스 세션입니다.

    Returns:
        RedirectResponse: 원래의 긴 URL로 리디렉션합니다.

    Raises:
        HTTPException: URL이 존재하지 않는 경우 404 오류를 반환합니다.
    """
    db_url = await crud.get_url_by_short_url(db, short_url)
    if db_url:
        await crud.increment_view_count(db, short_url)  # 조회 수 증가
        return RedirectResponse(url=db_url.url, status_code=301)
    else:
        raise HTTPException(status_code=404, detail="URL not found")

@app.get("/stats/{short_url}")
async def get_stats(short_url: str, db: AsyncSession = Depends(get_db)):
    """
    단축 URL의 조회 수를 반환합니다.

    제공된 단축 URL의 조회 수를 데이터베이스에서 조회하여 반환합니다.

    Args:
        short_url (str): 조회 수를 가져올 단축 URL입니다.
        db (AsyncSession): 데이터베이스 세션입니다.

    Returns:
        dict: 단축 URL과 조회 수를 포함한 사전입니다.

    Raises:
        HTTPException: URL이 존재하지 않는 경우 404 오류를 반환합니다.
    """
    view_count = await crud.get_view_count(db, short_url)
    if view_count is not None:
        return {"short_url": short_url, "view_count": view_count}
    else:
        raise HTTPException(status_code=404, detail="URL not found")

