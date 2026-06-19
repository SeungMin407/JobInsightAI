import json
import os
import sqlite3

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

# --------------------------------
# DB 생성
# --------------------------------

conn = sqlite3.connect("jobs.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    company TEXT,
    url TEXT,
    embedding_similarity REAL,
    score INTEGER,
    summary TEXT,
    matched_skills TEXT,
    missing_skills TEXT,
    reason TEXT
)
""")

# 기존 결과 삭제
cursor.execute(
    "DELETE FROM recommendations"
)

conn.commit()

# --------------------------------
# 프로필
# --------------------------------

with open(
    "profile.json",
    "r",
    encoding="utf-8"
) as f:

    profile = json.load(f)

# --------------------------------
# 임베딩 결과
# --------------------------------

with open(
    "ranked_jobs.json",
    "r",
    encoding="utf-8"
) as f:

    jobs = json.load(f)

# 상위 10개만 분석
jobs = jobs[:10]

# --------------------------------
# 프로필 요약
# --------------------------------

profile_summary = f"""
전공
{profile['education']['major']}

보유 기술
{", ".join(profile['skills'])}

사용 도구
{", ".join(profile['tools'])}

AI 분야
{", ".join(profile['ai_domains'])}

로보틱스 경험
{", ".join(profile['robotics'])}

프로젝트
"""

for project in profile["projects"]:

    profile_summary += f"""

- {project['name']}
기술: {", ".join(project['keywords'])}
"""

results = []

# --------------------------------
# 공고 분석
# --------------------------------

for idx, job in enumerate(jobs):

    print()
    print("=" * 50)
    print(f"[{idx+1}/{len(jobs)}]")
    print(job["title"])

    description = job["description"][:3000]

    prompt = f"""
당신은 AI 채용 담당자다.

지원자 정보

{profile_summary}

공고 정보

{description}

임베딩 적합도
{job["similarity"]:.4f}

평가 규칙

1.
실제 기술스택 기준으로 평가

2.
동일 의미 기술은 매칭 가능

예시

ML = Machine Learning
CV = Computer Vision
RL = Reinforcement Learning
LLM Agent = Agent Framework

3.
필수 기술 없으면 감점

4.
우대 기술은 가점

5.
점수는 보수적으로 평가

점수 기준

90~100
즉시 투입 가능

70~89
핵심 기술 다수 보유

50~69
관련 전공 + 일부 기술 보유

30~49
일부만 관련

0~29
거의 무관

반드시 JSON만 출력

{{
    "score": 0,
    "summary": "",
    "matched_skills": [],
    "missing_skills": [],
    "reason": ""
}}
"""

    try:

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            temperature=0.1,
            response_format={
                "type": "json_object"
            },
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        text = response.choices[0].message.content

        result = json.loads(text)

        print(
            f"점수: {result['score']}"
        )

        item = {

            "title": job["title"],
            "company": job["company"],
            "url": job["url"],

            "embedding_similarity":
            round(job["similarity"], 4),

            "score":
            result["score"],

            "summary":
            result["summary"],

            "matched_skills":
            result["matched_skills"],

            "missing_skills":
            result["missing_skills"],

            "reason":
            result["reason"]

        }

        results.append(item)

        # ------------------------
        # SQLite 저장
        # ------------------------

        cursor.execute(
            """
            INSERT INTO recommendations
            (
                title,
                company,
                url,
                embedding_similarity,
                score,
                summary,
                matched_skills,
                missing_skills,
                reason
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                item["title"],
                item["company"],
                item["url"],
                item["embedding_similarity"],
                item["score"],
                item["summary"],
                json.dumps(
                    item["matched_skills"],
                    ensure_ascii=False
                ),
                json.dumps(
                    item["missing_skills"],
                    ensure_ascii=False
                ),
                item["reason"]
            )
        )

        conn.commit()

    except Exception as e:

        print("ERROR:", e)

# --------------------------------
# 정렬
# --------------------------------

results.sort(
    key=lambda x: x["score"],
    reverse=True
)

# --------------------------------
# JSON 저장
# --------------------------------

with open(
    "recommendations.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        results,
        f,
        ensure_ascii=False,
        indent=4
    )

# --------------------------------
# 출력
# --------------------------------

print()
print("=" * 50)
print("최종 TOP 10")
print("=" * 50)

for item in results:

    print(
        f"{item['score']:3d}점 | "
        f"{item['company']} | "
        f"{item['title']}"
    )

print()
print("recommendations.json 저장 완료")
print("jobs.db 저장 완료")

conn.close()