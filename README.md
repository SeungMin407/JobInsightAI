# Job Insight
<img width="1113" height="768" alt="image" src="https://github.com/user-attachments/assets/bac987e6-5aa6-4a12-a853-ab6c42b91f74" />

AI 기반 채용공고 추천 및 적합도 분석 플랫폼

Job Insight는 채용공고를 자동으로 수집하고, 지원자 프로필과의 의미적 유사도를 계산한 뒤, LLM을 활용하여 실제 적합도를 분석하여 추천 결과를 제공하는 서비스입니다.

---

# 프로젝트 개요

기존 채용 플랫폼은 키워드 기반 검색에 의존하기 때문에 지원자의 실제 역량과 공고 요구사항 간의 정교한 매칭이 어렵습니다.

본 프로젝트는 다음과 같은 문제를 해결하기 위해 개발되었습니다.

- 채용공고 자동 수집
- 의미 기반(Semantic Search) 적합도 계산
- LLM 기반 정성 평가
- 맞춤형 추천 결과 제공
- 웹 기반 조회 서비스

---

# 시스템 아키텍처

```text
Saramin

 ↓

Playwright Crawler
(crawler.py)

 ↓

Job Detail Crawler
(detail_crawler.py)

 ↓

jobs_detail.json

 ↓

Sentence Transformer
(embedding_ranker.py)

 ↓

Embedding Ranking

 ↓

Groq LLM
(analyzer.py)

 ↓

Fit Analysis

 ↓

SQLite Database

 ↓

FastAPI

 ↓

Web Dashboard
```

---

# 주요 기능

## 1. 채용공고 수집

Playwright를 활용하여 사람인(Saramin)의 채용공고를 자동 수집합니다.

수집 정보

- 회사명
- 공고명
- 공고 URL

생성 파일

```text
jobs.json
```

---

## 2. 상세 공고 크롤링

공고 상세 페이지에 접근하여 실제 채용 내용을 수집합니다.

수집 정보

- 직무 내용
- 자격 요건
- 우대 사항
- 기술 스택

생성 파일

```text
jobs_detail.json
```

---

## 3. 임베딩 기반 적합도 계산

Sentence Transformers를 활용하여

- 지원자 프로필
- 채용공고

를 벡터화한 후 Cosine Similarity를 계산합니다.

사용 모델

```text
jhgan/ko-sroberta-multitask
```

계산 방식

```text
Candidate Profile Embedding
            ↓
      Cosine Similarity
            ↓
 Job Description Embedding
```

생성 파일

```text
ranked_jobs.json
```

예시

```json
{
  "title": "AI Engineer",
  "similarity": 0.73
}
```

---

## 4. LLM 기반 적합도 평가

임베딩 점수만으로는 실제 적합도를 판단하기 어렵기 때문에 LLM을 활용하여 정성 평가를 수행합니다.

사용 모델

```text
Llama 3.3 70B
(Groq API)
```

평가 기준

- 기술 스택 매칭 여부
- 프로젝트 경험
- 직무 적합성
- 부족 기술
- 실제 투입 가능성

출력 예시

```json
{
  "score": 85,
  "matched_skills": [
    "Python",
    "LLM",
    "Machine Learning"
  ],
  "missing_skills": [
    "Azure OpenAI",
    "Power Platform"
  ]
}
```

생성 파일

```text
recommendations.json
```

---

## 5. SQLite 저장

분석 결과를 SQLite에 저장합니다.

DB

```text
jobs.db
```

테이블

```sql
recommendations
```

컬럼

| 컬럼 | 설명 |
|--------|--------|
| id | PK |
| title | 공고명 |
| company | 회사명 |
| url | 공고 링크 |
| embedding_similarity | 임베딩 점수 |
| score | LLM 점수 |
| summary | 요약 |
| matched_skills | 보유 기술 |
| missing_skills | 부족 기술 |
| reason | 평가 근거 |

---

## 6. FastAPI 서비스

분석 결과를 REST API 형태로 제공합니다.

### 추천 결과 조회

```http
GET /recommendations
```

---

### 개별 공고 조회

```http
GET /job/{id}
```

---

### 전체 분석 실행

```http
POST /analyze
```

실행 순서

```text
crawler.py

↓

detail_crawler.py

↓

embedding_ranker.py

↓

analyzer.py

↓

DB 저장
```

---

## 7. 웹 대시보드

FastAPI + Jinja2 기반으로 구현

제공 기능

- TOP 10 추천 공고 조회
- 적합도 점수 표시
- 보유 기술 확인
- 부족 기술 확인
- 사람인 공고 바로가기

---

# 기술 스택

## Backend

- Python
- FastAPI

## Crawling

- Playwright

## AI

- Sentence Transformers
- Groq LLM
- Llama 3.3 70B

## Database

- SQLite

## Deployment

- Docker

## Template Engine

- Jinja2

---

# 프로젝트 구조

```text
job_insight/

├── app.py
├── crawler.py
├── detail_crawler.py
├── embedding_ranker.py
├── analyzer.py

├── profile.json

├── jobs.json
├── jobs_detail.json
├── ranked_jobs.json
├── recommendations.json

├── jobs.db

├── requirements.txt
├── Dockerfile

├── templates/
│   └── index.html

└── README.md
```

---

# 실행 방법

## 1. 저장소 클론

```bash
git clone https://github.com/your-id/job-insight.git

cd job-insight
```

---

## 2. 패키지 설치

```bash
pip install -r requirements.txt
```

---

## 3. 환경 변수 설정

`.env`

```env
GROQ_API_KEY=YOUR_API_KEY
```

---

## 4. 분석 실행

```bash
python crawler.py

python detail_crawler.py

python embedding_ranker.py

python analyzer.py
```

---

## 5. 서버 실행

```bash
uvicorn app:app --reload
```

접속

```text
http://127.0.0.1:8000
```

Swagger

```text
http://127.0.0.1:8000/docs
```

---

# Docker 실행

이미지 빌드

```bash
docker build -t job-insight .
```

실행

```bash
docker run -p 8000:8000 job-insight
```

접속

```text
http://localhost:8000
```

---

# 향후 개선 사항

- Redis 캐싱
- 사용자별 프로필 관리
- 실시간 공고 갱신
- RAG 기반 공고 분석
- Cloud 배포(AWS, GCP)

---

# 성과

- Playwright 기반 크롤링 자동화
- 의미 기반 채용공고 추천 시스템 구현
- LLM 기반 적합도 평가 자동화
- FastAPI REST API 구축
- SQLite 데이터 저장
- Docker 기반 서비스 배포 환경 구축

---

# Author

이승민

AI Engineer / LLM Engineer / Robotics Software Engineer
