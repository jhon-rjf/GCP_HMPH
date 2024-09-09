# HMPH (HowManyPeopleHere)

## Introduction
This project was conducted as part of the Google Cloud-based AI Professional Training Program (Advanced Course) at the K-High Tech Platform Division of Andong National University. The goal was to utilize GCP features for project implementation.

HMPH is a system that uses CCTV cameras installed in narrow alleys (simulated with Raspberry Pi) to monitor the number of people in the area and issue warnings based on crowd density.

## Presentation
For a detailed presentation of this project, please view:

![GoogleSlide](https://github.com/user-attachments/assets/0c0773f5-829d-4bd6-a89f-bfd5ff039973)

[View Presentation](https://docs.google.com/presentation/d/13FEeBHMOEWEBfjOnqBWsbE8tzCHNL2oqJx4HA8yl5AY/edit?usp=sharing)

## Key GCP Features Used
- Google Dataflow
- Google Pub/Sub
- Google BigQuery
- Google Cloud Storage
- Google Vertex AI
- Google Gemini
- Google Compute Engine
- Google Looker Studio

## Context Diagram
![Context_Diagram](https://github.com/user-attachments/assets/62664bf3-ffc1-4f11-a46a-115bdaf9b841)

## Development Environment
All services operate within the Google Cloud Platform ecosystem.

## Installation
1. Create a GCP project and set up a virtual machine in Compute Engine to run the Flask app.
2. Modify the relevant IDs in `app.py` to enable the use of corresponding services.

*Note: Other content differing from the PPT file pertains to other team members' development areas.*

## Usage
1. Run `app.py`.
2. Input the area when prompted.
3. The web interface and BigQuery systems will activate.
4. Access the website using the VM's external IP address on port 8000.

## Award: Best AI Convergence Award at the AI Convergence Innovation Technology Competition
This project received the Best AI Convergence Award at the Google Cloud AI Professional Training Program's AI Convergence Innovation Technology Competition.

[University News Article](https://www.anu.ac.kr/main/board/view.do?menu_idx=72&manage_idx=1&search.category1=106&board_idx=222242)

![Award Ceremony and Presentation](https://github.com/user-attachments/assets/9e453b28-a5c6-46db-a53a-9d09c3ccb4be)

## Contact
We welcome questions and feedback!
Email: [ykjung0917@kakao.com]

---

# HMPH (HowManyPeopleHere)

## 소개
이 프로젝트는 국립안동대학교 GoogleCloud 기반 인공지능 전문인력 양성과정(고급반)에서 진행한 프로젝트로, GCP의 기능을 사용하여 프로젝트를 하는것이 목표입니다.
좁은 골목등에 설치된 cctv를 기반(RPI대체)으로 해당 골목에 얼마나 많은 유동인구가 있는지 확인해서 경고를 하는 시스템입니다.

## 프레젠테이션
아래는 이 프로젝트에 대한 상세한 프레젠테이션입니다:

![GoogleSlide](https://github.com/user-attachments/assets/0c0773f5-829d-4bd6-a89f-bfd5ff039973)
[프레젠테이션 보기](https://docs.google.com/presentation/d/13FEeBHMOEWEBfjOnqBWsbE8tzCHNL2oqJx4HA8yl5AY/edit?usp=sharing)

## 주요사용 GCP  기능
- Google Dataflow
- Google Google pubsub
- Google BigQuery
- Google Cloud Storage
- Google Vertex AI
- Google Gemini
- Google Compute engine
- Google Looker Studio

## Context Diagram
![Context_Diagram](https://github.com/user-attachments/assets/62664bf3-ffc1-4f11-a46a-115bdaf9b841)

## 개발환경
모든 서비스의 동작은 GCP에서 동작하는 시스템입니다.

## 설치 방법
1. GCP project 생성 이후 Compute engine에서 virtual machine 하나를 만들어 flask app을 동작시킵니다.
2. app.py에서 각 해당 란의 ID들을 수정하여 해당 서비스를 사용하게 한다.

* 위 ppt파일과 다른 내용은 다른 팀원의 개발 분야입니다.


## 사용 방법
app.py를 실행, 면적입력하면 web과 bigquery등의 시스템이 동작합니다.
vm의 외부 ip주소를 활용하여 포트 8000번으로 웹사이트에 진입합니다.

## Google Cloud 인공지능 전문인력 양성과정 AI 융합혁신 기술대회 최우수 AI융합상

[교내소식](https://www.anu.ac.kr/main/board/view.do?menu_idx=72&manage_idx=1&search.category1=106&board_idx=222242)

![대회 최우수상 수여 및 발표현장](https://github.com/user-attachments/assets/9e453b28-a5c6-46db-a53a-9d09c3ccb4be)


## 연락처
질문이나 피드백을 환영합니다 
제 이메일 입니다. ykjung0917@kakao.com 
