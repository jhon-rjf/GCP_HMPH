# 기본 이미지로 Python 3.11를 사용
FROM apache/beam_python3.11_sdk:2.58.0

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

# 작업을 위한 추가 파일이나 코드를 복사할 수 있습니다
COPY . .

# Dataflow에서 실행될 때 기본적으로 실행할 스크립트를 지정합니다.
ENTRYPOINT ["python", "your_dataflow_pipeline.py"]
