import json
import sqlite3
import subprocess

from fastapi import FastAPI, HTTPException, Request
from fastapi.templating import Jinja2Templates

DB_NAME = "jobs.db"

app = FastAPI()

templates = Jinja2Templates(
    directory="templates"
)

# --------------------------
# DB 조회 함수
# --------------------------

def get_recommendations():

    conn = sqlite3.connect(DB_NAME)

    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM recommendations
        ORDER BY score DESC
        """
    )

    rows = cursor.fetchall()

    conn.close()

    jobs = []

    for row in rows:

        item = dict(row)

        try:
            item["matched_skills"] = json.loads(
                item["matched_skills"]
            )
        except:
            item["matched_skills"] = []

        try:
            item["missing_skills"] = json.loads(
                item["missing_skills"]
            )
        except:
            item["missing_skills"] = []

        jobs.append(item)

    return jobs


# --------------------------
# 메인 페이지
# --------------------------

@app.get("/")
def home(request: Request):

    try:

        jobs = get_recommendations()

    except Exception as e:

        print(e)

        jobs = []

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "jobs": jobs[:10]
        }
    )


# --------------------------
# 추천 결과 API
# --------------------------

@app.get("/recommendations")
def recommendations():

    try:

        return get_recommendations()[:10]

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# --------------------------
# 개별 공고 API
# --------------------------

@app.get("/job/{job_id}")
def get_job(job_id: int):

    conn = sqlite3.connect(DB_NAME)

    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM recommendations
        WHERE id = ?
        """,
        (job_id,)
    )

    row = cursor.fetchone()

    conn.close()

    if row is None:

        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    job = dict(row)

    try:

        job["matched_skills"] = json.loads(
            job["matched_skills"]
        )

    except:

        job["matched_skills"] = []

    try:

        job["missing_skills"] = json.loads(
            job["missing_skills"]
        )

    except:

        job["missing_skills"] = []

    return job


# --------------------------
# 전체 분석 실행
# --------------------------

@app.post("/analyze")
def analyze():

    try:

        print("1. 공고 수집 시작")

        subprocess.run(
            ["python", "crawler.py"],
            check=True
        )

        print("2. 상세 공고 수집 시작")

        subprocess.run(
            ["python", "detail_crawler.py"],
            check=True
        )

        print("3. 임베딩 랭킹 시작")

        subprocess.run(
            ["python", "embedding_ranker.py"],
            check=True
        )

        print("4. LLM 분석 시작")

        subprocess.run(
            ["python", "analyzer.py"],
            check=True
        )

        return {
            "status": "success",
            "message": "전체 분석 완료"
        }

    except subprocess.CalledProcessError as e:

        raise HTTPException(
            status_code=500,
            detail=f"실행 실패: {e}"
        )


# --------------------------
# 실행
# --------------------------

# uvicorn app:app --reload
# http://127.0.0.1:8000
# http://127.0.0.1:8000/recommendations
# http://127.0.0.1:8000/docs
# http://127.0.0.1:8000/job/1