# 베이스 이미지를 선택합니다.
FROM python:3.9-slim

# 작업 디렉토리를 설정합니다.
WORKDIR /app

# 시스템 패키지를 업데이트하고 필요한 라이브러리들을 설치합니다.
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    build-essential \
    --no-install-recommends && rm -rf /var/lib/apt/lists/*

# 필요한 파일들을 복사합니다.
COPY requirements.txt .

# pip 및 필수 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 소스 코드를 복사합니다.
COPY . .

# 포트를 환경 변수로 설정합니다.
ENV PORT=8000

# ENTRYPOINT를 설정하여 기본 실행 명령을 지정합니다.
ENTRYPOINT ["python", "app.py"]

# CMD는 기본 인자를 설정합니다.
CMD ["3", "1"]

