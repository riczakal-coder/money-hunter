# ============================================================
# Dockerfile — Money Hunter Backend Server
# Maintainer: Young-cheol (Backend Engineer)
# ============================================================
# 1. Base Image: 경량화된 Python 3.11 사용
FROM python:3.11-slim

# 2. 시스템 패키지 설치 & Timezone 설정 (Asia/Seoul)
# Timezone 설정이 안 되면 스케줄러가 UTC 기준(9시간 느림)으로 동작함
RUN apt-get update && apt-get install -y --no-install-recommends tzdata \
    && ln -snf /usr/share/zoneinfo/Asia/Seoul /etc/localtime \
    && echo "Asia/Seoul" > /etc/timezone \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 3. 작업 디렉토리 설정
WORKDIR /app

# 4. 의존성 설치
# requirements.txt만 먼저 복사하여 캐시를 활용
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. 소스 코드 복사
# .dockerignore에 정의된 파일들은 복사되지 않음
COPY . .

# 6. 실행 명령어
# FastAPI 서버 실행 (0.0.0.0으로 열어야 외부 접속 가능)
CMD ["uvicorn", "src.backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
