import json

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# -------------------------
# 모델 로드
# -------------------------

model = SentenceTransformer(
    "jhgan/ko-sroberta-multitask"
)

# -------------------------
# 프로필 읽기
# -------------------------

with open(
    "profile.json",
    "r",
    encoding="utf-8"
) as f:

    profile = json.load(f)

# -------------------------
# 공고 읽기
# -------------------------

with open(
    "jobs_detail.json",
    "r",
    encoding="utf-8"
) as f:

    jobs = json.load(f)

# -------------------------
# 프로필 텍스트 생성
# -------------------------

profile_parts = []

profile_parts.extend(
    profile.get("skills", [])
)

profile_parts.extend(
    profile.get("tools", [])
)

profile_parts.extend(
    profile.get("robotics", [])
)

profile_parts.extend(
    profile.get("ai_domains", [])
)

profile_parts.extend(
    profile.get("interests", [])
)

for project in profile.get("projects", []):

    profile_parts.append(
        project.get("name", "")
    )

    profile_parts.extend(
        project.get("keywords", [])
    )

profile_text = " ".join(profile_parts)

print("프로필 길이:", len(profile_text))

# -------------------------
# 프로필 임베딩
# -------------------------

profile_embedding = model.encode(
    profile_text
)

# -------------------------
# 공고 임베딩
# -------------------------

results = []

for idx, job in enumerate(jobs):

    description = job.get(
        "description",
        ""
    ).strip()

    # 설명 없는 공고 제거
    if len(description) < 200:

        print(
            f"[SKIP] {job['title']} (내용 부족)"
        )

        continue

    try:

        job_embedding = model.encode(
            description
        )

        similarity = cosine_similarity(
            [profile_embedding],
            [job_embedding]
        )[0][0]

        results.append({

            "title": job["title"],
            "company": job["company"],
            "url": job["url"],
            "similarity": float(similarity),
            "description": description

        })

        print(
            f"[{idx+1}/{len(jobs)}] "
            f"{job['title']} "
            f"{similarity:.4f}"
        )

    except Exception as e:

        print(
            f"ERROR: {job['title']}"
        )

        print(e)

# -------------------------
# 유사도 정렬
# -------------------------

results.sort(
    key=lambda x: x["similarity"],
    reverse=True
)

# -------------------------
# 전체 저장
# -------------------------

with open(
    "ranked_jobs.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        results,
        f,
        ensure_ascii=False,
        indent=4
    )

# -------------------------
# TOP10 저장
# -------------------------

top_jobs = results[:10]

with open(
    "top_jobs.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        top_jobs,
        f,
        ensure_ascii=False,
        indent=4
    )

# -------------------------
# 출력
# -------------------------

print()
print("=" * 60)
print("추천 TOP 10")
print("=" * 60)

for rank, item in enumerate(top_jobs, start=1):

    print(
        f"{rank:2d}위 | "
        f"{item['similarity']:.4f} | "
        f"{item['company']} | "
        f"{item['title']}"
    )

print()
print("ranked_jobs.json 저장 완료")
print("top_jobs.json 저장 완료")