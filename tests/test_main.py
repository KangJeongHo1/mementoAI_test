import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from datetime import datetime

from app.main import app
from app import crud, schemas

client = TestClient(app)

@pytest.mark.asyncio
@patch("app.crud.create_url", new_callable=AsyncMock)
@patch("app.crud.get_url_by_short_url", new_callable=AsyncMock)
@patch("app.utils.generate_short_url", return_value="short1234")
async def test_create_short_url(mock_generate_short_url, mock_get_url_by_short_url, mock_create_url):
    # URL이 중복되지 않음을 확인
    mock_get_url_by_short_url.return_value = None
    # URL 생성 모킹
    mock_create_url.return_value = schemas.URL(
        id=1,
        url="http://example.com",
        short_url="short1234",
        expiration_date=datetime.fromisoformat("2024-12-31T00:00:00")
    )

    response = client.post("/shorten", json={"url": "http://example.com", "expiration_date": "2024-12-31T00:00:00"})
    assert response.status_code == 200
    data = response.json()
    assert data["short_url"] == "short1234"
    assert data["url"] == "http://example.com"

@pytest.mark.asyncio
@patch("app.crud.get_url_by_short_url", new_callable=AsyncMock)
@patch("app.crud.increment_view_count", new_callable=AsyncMock)
async def test_redirect_to_original_url(mock_increment_view_count, mock_get_url_by_short_url):
    # URL 조회 모킹
    mock_get_url_by_short_url.return_value = schemas.URL(
        id=1,
        url="http://example.com",
        short_url="short1234",
        expiration_date=datetime.fromisoformat("2024-12-31T00:00:00")
    )
    
    # `AsyncSession` 모킹
    mock_session = AsyncMock()
    
    # increment_view_count가 `AsyncSession`을 인자로 받을 것이라고 가정
    mock_increment_view_count.return_value = None  # 이 테스트에서는 반환 값을 사용하지 않음
    
    # 클라이언트에서의 요청 처리
    response = client.get("/short1234", allow_redirects=False)
    
    assert response.status_code == 301
    assert response.headers["location"] == "http://example.com"
    
    # 호출된 인자 확인 (두 번째 인자는 "short1234"여야 함)
    call_args = mock_increment_view_count.await_args
    assert call_args[0][1] == "short1234"


@pytest.mark.asyncio
@patch("app.crud.get_view_count", new_callable=AsyncMock)
async def test_get_stats(mock_get_view_count):
    # 조회 수 반환 모킹
    mock_get_view_count.return_value = 5

    response = client.get("/stats/short1234")
    assert response.status_code == 200
    data = response.json()
    assert data["short_url"] == "short1234"
    assert data["view_count"] == 5

@pytest.mark.asyncio
@patch("app.crud.get_url_by_short_url", new_callable=AsyncMock)
async def test_redirect_to_original_url_not_found(mock_get_url_by_short_url):
    # URL이 존재하지 않음을 모킹
    mock_get_url_by_short_url.return_value = None

    response = client.get("/short1234")
    assert response.status_code == 404
    assert response.json() == {"detail": "URL not found"}

@pytest.mark.asyncio
@patch("app.crud.get_view_count", new_callable=AsyncMock)
async def test_get_stats_not_found(mock_get_view_count):
    # 조회 수를 찾지 못함을 모킹
    mock_get_view_count.return_value = None

    response = client.get("/stats/short1234")
    assert response.status_code == 404
    assert response.json() == {"detail": "URL not found"}