# HMPH (HowManyPeopleHere)

## 소개
이 프로젝트는 국립안동대학교 GoogleCloud 기반 인공지능 전문인력 양성과정(고급반)에서 진행한 프로젝트로, GCP의 기능을 사용하여 프로젝트를 하는것이 목표입니다.
좁은 골목등에 설치된 cctv를 기반(RPI대체)으로 해당 골목에 얼마나 많은 유동인구가 있는지 확인해서 경고를 하는 시스템입니다.

## 프레젠테이션
아래는 이 프로젝트에 대한 상세한 프레젠테이션입니다:

[![GoogleSlide](![thumbnail](https://github.com/user-attachments/assets/0c0773f5-829d-4bd6-a89f-bfd5ff039973))](https://docs.google.com/presentation/d/13FEeBHMOEWEBfjOnqBWsbE8tzCHNL2oqJx4HA8yl5AY/edit?usp=sharing)

## 주요사용 GCP  기능
- Google Dataflow
- Google Google pubsub
- Google BigQuery
- Google Cloud Storage
- Google Vertex AI
- Google Gemini
- Google Compute engine
- Google Looker Studio

## 개발환경
모든 서비스의 동작은 GCP에서 동작하는 시스템입니다.

## 설치 방법
1. GCP project 생성 이후 Compute engine에서 virtual machine 하나를 만들어 flask app을 동작시킵니다.
2. app.py에서 각 해당 란의 ID들을 수정하여 해당 서비스를 사용하게 한다.

* 위 ppt파일과 다른 내용은 다른 팀원의 개발 분야입니다.


## 사용 방법
app.py를 실행, 면적입력하면 web과 bigquery등의 시스템이 동작합니다.
vm의 외부 ip주소를 활용하여 포트 8000번으로 웹사이트에 진입합니다.

## 연락처
질문이나 피드백을 환영합니다 
제 이매일 입니다. ykjung0917@kakao.com 
