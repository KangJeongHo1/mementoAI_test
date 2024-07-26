# mementoAI_test
## 긴 URL을 짧게 단축하여 사용하고, 단축된 URL을 통해 원본 URL로 리디렉션하는 기능 개발
#### 프레임워크 : FastAPI
#### 데이터베이스 : PostgreSQL - PostgreSQL은 성능, 확장성, 데이터 모델링의 유연성, 그리고 강력한 커스터마이징 기능 덕분에 단축 URL 서비스와 같은 대규모 애플리케이션에서 요구되는 다양한 요구 사항을 충족시킬 수 있음. 데이터의 무결성 및 일관성을 보장하며, 대량의 데이터와 높은 동시 사용량을 안정적으로 처리할 수 있는 강력한 데이터베이스 선택이므로 PostgreSQL을 채택했음

1. 깃 클론 및 가상환경 구성
   * 터미널에 git clone https://github.com/KangJeongHo1/mementoAI_test.git
   * 해당 폴더 진입 후 poetry shell 및 poetry install

2. .env 및 alembic.ini 파일에 데이터베이스 주소 수정
   * .env 파일에 접속 후 자신의 postgres 데이터베이스 이름, 패스워드에 맞춰서 URL 수정
   * alembic.ini 64번째 줄도 수정
   * alembic revision --autogenerate -m "initial migration" 으로 마이그레이트
   * alembic upgrade head 으로 마이그레이션 

  
3. 서버 실행
   * poetry run uvicorn app.main:app --reload 명령어를 입력하여 서버 실행
   * 127.0.0.1:8000/swagger, 127.0.0.1:8000/redoc 으로 문서 확인 가능
     * 리디렉션 되는 2번째 API에 경우 바로 홈페이지로 이동이 안되고 해당 홈페이지의 CSS 데이터를 가져옴.
     * 해당 경우엔 127.0.0.1:8000/{short_url}로 이동하면 해당 홈페이지 접속 가능
       
4. 보너스 기능
  * 과제 내에 있는 보너스 기능 개발 완료
  * UTC 시간으로 만료기간 처리. 한국시간 = UTC시간 + 9시간
  * main.py 테스트 코드 실행시 pytest tests/test_main.py/
  * crud.py 테스트 코드 실행시 pytest tests/test_crud.py/
