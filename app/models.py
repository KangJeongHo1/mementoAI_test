from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class URL(Base):
    __tablename__ = 'urls'

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, index=True)  # 원본 URL을 `url`로 변경
    short_url = Column(String, unique=True, index=True)
    expiration_date = Column(DateTime, nullable=True)  # 만료 날짜 필드 추가
