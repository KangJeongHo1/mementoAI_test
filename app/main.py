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
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    # 백그라운드 작업으로 만료된 URL 삭제
    async with engine.connect() as conn:
        await crud.delete_expired_urls(conn)

@app.post("/shorten", response_model=schemas.URL)
async def create_short_url(url: schemas.URLCreate, db: AsyncSession = Depends(get_db)):
    short_url = generate_short_url()
    while await crud.get_url_by_short_url(db, short_url):
        short_url = generate_short_url()
    db_url = await crud.create_url(db, url.url, short_url, url.expiration_date)
    return db_url

@app.get("/{short_url}", response_class=RedirectResponse)
async def redirect_to_original_url(short_url: str, db: AsyncSession = Depends(get_db)):
    db_url = await crud.get_url_by_short_url(db, short_url)
    if db_url:
        await crud.increment_view_count(db, short_url)  # 조회 수 증가
        return RedirectResponse(url=db_url.url, status_code=301)
    else:
        raise HTTPException(status_code=404, detail="URL not found")

@app.get("/stats/{short_url}")
async def get_stats(short_url: str, db: AsyncSession = Depends(get_db)):
    view_count = await crud.get_view_count(db, short_url)
    if view_count is not None:
        return {"short_url": short_url, "view_count": view_count}
    else:
        raise HTTPException(status_code=404, detail="URL not found")
