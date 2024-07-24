from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Url(Base):
    __tablename__ = 'urls'

    id = Column(Integer, primary_key=True)
    short_url = Column(String(50), nullable=False, unique=True)
    long_url = Column(String(2048), nullable=False)

    def __repr__(self):
        return '<Url %r>' % self.short_url

