import pytest
import unittest

from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, patch, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import delete
from datetime import datetime, timedelta
from app import crud, models
from app.crud import get_url_by_short_url, get_view_count, delete_expired_urls

@pytest.mark.asyncio
@patch('app.crud.AsyncSession', autospec=True)
async def TestCreateUrl(mock_session_class):
    """
    create_url 함수 테스트:
    - 데이터베이스에 새로운 URL을 생성하는 함수입니다.
    - 이 테스트에서는 데이터베이스 세션을 모의 객체로 대체하고, 함수 호출 후 URL 객체가 올바르게 반환되는지 확인합니다.
    """
    mock_session = mock_session_class.return_value
    mock_add = AsyncMock()
    mock_commit = AsyncMock()
    mock_refresh = AsyncMock()
    mock_session.add = mock_add
    mock_session.commit = mock_commit
    mock_session.refresh = mock_refresh

    url_to_create = "https://example.com"
    short_url = "shorty"
    expiration_date = None

    # Mock URL 객체 생성
    mock_instance = MagicMock(spec=models.URL)
    mock_instance.url = url_to_create
    mock_instance.short_url = short_url
    mock_instance.expiration_date = expiration_date

    with patch('app.crud.models.URL', return_value=mock_instance):
        # create_url 함수 호출
        response = await crud.create_url(mock_session, url_to_create, short_url, expiration_date)

        # 함수 호출 후 검증
        mock_add.assert_called_once_with(mock_instance)
        mock_commit.assert_called_once()
        mock_refresh.assert_called_once()
        assert response.url == url_to_create
        assert response.short_url == short_url
        assert response.expiration_date is None



class TestGetUrlByShortUrl(unittest.IsolatedAsyncioTestCase):
    async def test_get_url_by_short_url_valid(self):
        """
        유효한 short_url을 테스트:
        - 만료되지 않은 URL을 반환해야 합니다.
        """
        # 데이터베이스 세션과 결과를 모의 객체로 생성
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_db.execute.return_value = mock_result

        # 모의 URL 객체 생성 및 만료 날짜 설정
        mock_url = MagicMock()
        mock_url.expiration_date = datetime.utcnow() + timedelta(days=1)
        mock_result.scalars.return_value.first.return_value = mock_url

        # get_url_by_short_url 함수 호출
        result = await get_url_by_short_url(mock_db, "short_url")

        # 함수 호출 후 검증
        mock_db.execute.assert_called_once()  # execute 메서드가 한 번 호출되었는지 확인
        self.assertIsNotNone(result)  # 반환값이 None이 아닌지 확인
        self.assertEqual(result, mock_url)  # 반환값이 예상한 URL 객체인지 확인
    
    async def test_get_url_by_short_url_expired(self):
        """
        만료된 short_url을 테스트:
        - 만료된 URL은 None을 반환해야 합니다.
        """
        # 데이터베이스 세션과 결과를 모의 객체로 생성
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_db.execute.return_value = mock_result

        # 모의 URL 객체 생성 및 만료 날짜 설정
        mock_url = MagicMock()
        mock_url.expiration_date = datetime.utcnow() - timedelta(days=1)
        mock_result.scalars.return_value.first.return_value = mock_url

        # get_url_by_short_url 함수 호출
        result = await get_url_by_short_url(mock_db, "short_url")

        # 함수 호출 후 검증
        mock_db.execute.assert_called_once()  # execute 메서드가 한 번 호출되었는지 확인
        self.assertIsNone(result)  # 반환값이 None인지 확인

    async def test_get_url_by_short_url_no_expiry(self):
        """
        만료 날짜가 없는 short_url을 테스트:
        - 만료 날짜가 없는 URL은 유효한 것으로 간주하여 반환해야 합니다.
        """
        # 데이터베이스 세션과 결과를 모의 객체로 생성
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_db.execute.return_value = mock_result

        # 모의 URL 객체 생성 및 만료 날짜 설정
        mock_url = MagicMock()
        mock_url.expiration_date = None
        mock_result.scalars.return_value.first.return_value = mock_url

        # get_url_by_short_url 함수 호출
        result = await get_url_by_short_url(mock_db, "short_url")

        # 함수 호출 후 검증
        mock_db.execute.assert_called_once()  # execute 메서드가 한 번 호출되었는지 확인
        self.assertIsNotNone(result)  # 반환값이 None이 아닌지 확인
        self.assertEqual(result, mock_url)  # 반환값이 예상한 URL 객체인지 확인
    
    async def test_get_url_by_short_url_not_found(self):
        """
        존재하지 않는 short_url을 테스트:
        - 존재하지 않는 URL은 None을 반환해야 합니다.
        """
        # 데이터베이스 세션과 결과를 모의 객체로 생성
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_db.execute.return_value = mock_result

        # 모의 URL 객체가 반환되지 않도록 설정
        mock_result.scalars.return_value.first.return_value = None

        # get_url_by_short_url 함수 호출
        result = await get_url_by_short_url(mock_db, "short_url")

        # 함수 호출 후 검증
        mock_db.execute.assert_called_once()  # execute 메서드가 한 번 호출되었는지 확인
        self.assertIsNone(result)  # 반환값이 None인지 확인



class TestGetViewCount(IsolatedAsyncioTestCase):
    async def test_get_view_count_valid(self):
        """
        유효한 short_url에 대한 조회 수 반환 테스트:
        - 올바른 조회 수가 반환되어야 합니다.
        """
        # 데이터베이스 세션과 URL 객체를 모의 객체로 생성
        mock_db = AsyncMock(spec=AsyncSession)
        mock_result = MagicMock()
        mock_db.execute.return_value = mock_result

        # 모의 URL 객체 생성 및 조회 수 설정
        mock_url = MagicMock()
        mock_url.view_count = 5
        mock_result.scalars.return_value.first.return_value = mock_url

        # get_view_count 함수 호출
        view_count = await get_view_count(mock_db, "short_url")

        # 함수 호출 후 검증
        mock_db.execute.assert_called_once()  # execute 메서드가 한 번 호출되었는지 확인
        self.assertEqual(view_count, 5)  # 조회 수가 올바르게 반환되었는지 확인

    async def test_get_view_count_not_found(self):
        """
        존재하지 않는 short_url에 대한 조회 수 반환 테스트:
        - URL이 존재하지 않으면 None이 반환되어야 합니다.
        """
        # 데이터베이스 세션과 URL 객체를 모의 객체로 생성
        mock_db = AsyncMock(spec=AsyncSession)
        mock_result = MagicMock()
        mock_db.execute.return_value = mock_result

        # 모의 URL 객체가 반환되지 않도록 설정
        mock_result.scalars.return_value.first.return_value = None

        # get_view_count 함수 호출
        view_count = await get_view_count(mock_db, "short_url")

        # 함수 호출 후 검증
        mock_db.execute.assert_called_once()  # execute 메서드가 한 번 호출되었는지 확인
        self.assertIsNone(view_count)  # 반환된 값이 None인지 확인

    async def test_get_view_count_none_view_count(self):
        """
        조회 수가 None인 short_url에 대한 조회 수 반환 테스트:
        - 조회 수가 None인 경우에도 None이 반환되어야 합니다.
        """
        # 데이터베이스 세션과 URL 객체를 모의 객체로 생성
        mock_db = AsyncMock(spec=AsyncSession)
        mock_result = MagicMock()
        mock_db.execute.return_value = mock_result

        # 모의 URL 객체 생성 및 조회 수를 None으로 설정
        mock_url = MagicMock()
        mock_url.view_count = None
        mock_result.scalars.return_value.first.return_value = mock_url

        # get_view_count 함수 호출
        view_count = await get_view_count(mock_db, "short_url")

        # 함수 호출 후 검증
        mock_db.execute.assert_called_once()  # execute 메서드가 한 번 호출되었는지 확인
        self.assertIsNone(view_count)  # 반환된 값이 None인지 확인



class TestDeleteExpiredUrls(unittest.IsolatedAsyncioTestCase):
    @patch('app.crud.datetime')
    async def test_delete_expired_urls(self, mock_datetime):
        """
        만료된 URL 항목 삭제 테스트:
        - 만료된 URL 항목이 올바르게 삭제되어야 합니다.
        """
        # 현재 시간을 모의 객체로 설정
        now = datetime(2024, 7, 26)
        mock_datetime.utcnow.return_value = now

        # 데이터베이스 세션을 모의 객체로 생성
        mock_db = AsyncMock(spec=AsyncSession)

        # delete_expired_urls 함수 호출
        await delete_expired_urls(mock_db)

        # 함수 호출 후 검증
        stmt = delete(models.URL).where(models.URL.expiration_date < now)
        
        # Mock 객체의 호출 인자를 추출하고 확인
        args, kwargs = mock_db.execute.call_args
        actual_stmt = args[0]
        
        # 직접 쿼리 비교
        self.assertEqual(str(stmt), str(actual_stmt), f"Expected: {stmt}, Actual: {actual_stmt}")

        mock_db.commit.assert_called_once()  # 트랜잭션 커밋이 한 번 호출되었는지 확인

    @patch('app.crud.datetime')
    async def test_no_expired_urls(self, mock_datetime):
        """
        만료된 URL 항목이 없는 경우 테스트:
        - 삭제되는 항목이 없어야 합니다.
        """
        # 현재 시간을 모의 객체로 설정
        now = datetime(2024, 7, 26)
        mock_datetime.utcnow.return_value = now

        # 데이터베이스 세션을 모의 객체로 생성
        mock_db = AsyncMock(spec=AsyncSession)

        # delete_expired_urls 함수 호출
        await delete_expired_urls(mock_db)

        # 함수 호출 후 검증
        stmt = delete(models.URL).where(models.URL.expiration_date < now)

        # Mock 객체의 호출 인자를 추출하고 확인
        args, kwargs = mock_db.execute.call_args
        actual_stmt = args[0]
        
        # 직접 쿼리 비교
        self.assertEqual(str(stmt), str(actual_stmt), f"Expected: {stmt}, Actual: {actual_stmt}")

        mock_db.commit.assert_called_once()  # 트랜잭션 커밋이 한 번 호출되었는지 확인