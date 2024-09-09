# 기본 이미지로 Python 3.11을 사용
FROM apache/beam_python3.11.2_sdk:2.57

# 필요한 시스템 패키지를 설치
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 작업 디렉토리 설정
WORKDIR /app

# requirements.txt 파일을 이미지에 복사
COPY requirements.txt .

# Python 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt

#기본 스크립트 지정
ENTRYPOINT ["python", "pipline_doc.py"]
