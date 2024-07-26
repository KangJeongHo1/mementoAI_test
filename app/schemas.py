from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class URLCreate(BaseModel):
    """
    URL을 생성하기 위한 데이터 모델입니다.

    긴 URL과 선택적으로 만료 날짜를 포함할 수 있습니다. 이 모델은 사용자가
    긴 URL과 선택적으로 만료 날짜를 제공하여 단축 URL을 생성할 때 사용됩니다.

    Attributes:
        url (str): 사용자가 단축하려는 원본 URL입니다.
        expiration_date (Optional[datetime]): URL의 만료 날짜입니다. 만료 날짜를
        제공하지 않으면 `None`으로 설정됩니다.
    """
    url: str  # 원본 URL을 `url`로 변경
    expiration_date: Optional[datetime] = None  # 만료 날짜 선택적 추가

class URL(BaseModel):
    """
    단축된 URL에 대한 데이터 모델입니다.

    이 모델은 데이터베이스에서 조회된 URL 정보를 포함합니다. 단축 URL, 원본
    URL, 만료 날짜와 같은 정보를 포함하며, 이를 통해 URL 관련 정보를 반환합니다.

    Attributes:
        id (int): URL 항목의 고유 식별자입니다.
        url (str): 원본 URL입니다.
        short_url (str): 생성된 단축 URL입니다.
        expiration_date (Optional[datetime]): URL의 만료 날짜입니다. 만료 날짜가
        설정되지 않은 경우 `None`으로 설정됩니다.
    """
    id: int
    url: str  # 원본 URL을 `url`로 변경
    short_url: str
    expiration_date: Optional[datetime]

    class Config:
        """
        Pydantic 모델의 구성 설정을 정의합니다.

        orm_mode를 `True`로 설정하여 ORM 객체를 Pydantic 모델로 자동 변환할 수
        있게 합니다. 이를 통해 데이터베이스 모델과 Pydantic 모델 간의 변환이
        원활하게 이루어질 수 있습니다.
        """
        orm_mode = True
