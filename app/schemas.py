from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class URLCreate(BaseModel):
    url: str  # 원본 URL을 `url`로 변경
    expiration_date: Optional[datetime] = None  # 만료 날짜 선택적 추가

class URL(BaseModel):
    id: int
    url: str  # 원본 URL을 `url`로 변경
    short_url: str
    expiration_date: Optional[datetime]

    class Config:
        orm_mode = True
