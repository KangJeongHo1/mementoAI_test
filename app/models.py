from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import expression
from sqlalchemy.orm import relationship
import pytz
from datetime import datetime

Base = declarative_base()

class URL(Base):
    __tablename__ = 'urls'

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, nullable=False)
    short_url = Column(String, unique=True, index=True, nullable=False)
    expiration_date = Column(DateTime, nullable=True)
    view_count = Column(Integer, default=0)  # 조회 수를 저장할 필드 추가
