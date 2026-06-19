import json
from playwright.sync_api import sync_playwright

with open(
    "jobs.json",
    "r",
    encoding="utf-8"
) as f:
    jobs = json.load(f)

results = []

with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=False
    )

    page = browser.new_page()

    for idx, job in enumerate(jobs):

        print("=" * 50)
        print(f"[{idx+1}/{len(jobs)}]")
        print(job["title"])

        try:

            page.goto(
                job["url"],
                timeout=60000
            )

            page.wait_for_timeout(3000)

            detail_text = ""

            # -------------------
            # 방법1
            # iframe src 직접 접속
            # -------------------

            iframe = page.locator(
                "iframe.iframe_content"
            )

            if iframe.count() > 0:

                src = iframe.first.get_attribute(
                    "src"
                )

                if src:

                    detail_url = (
                        "https://www.saramin.co.kr"
                        + src
                    )

                    detail_page = browser.new_page()

                    detail_page.goto(
                        detail_url,
                        timeout=60000
                    )

                    detail_page.wait_for_timeout(
                        2000
                    )

                    detail_text = (
                        detail_page
                        .locator("body")
                        .inner_text()
                    )

                    detail_page.close()

                    print(
                        "iframe 상세페이지 추출 성공"
                    )

            # -------------------
            # 방법2
            # 일반 공고
            # -------------------

            if len(detail_text.strip()) < 200:

                try:

                    detail_text = (
                        page
                        .locator(".user_content")
                        .inner_text()
                    )

                    print(
                        "user_content 추출 성공"
                    )

                except:
                    pass

            # -------------------
            # 방법3
            # body 전체
            # -------------------

            if len(detail_text.strip()) < 200:

                detail_text = (
                    page
                    .locator("body")
                    .inner_text()
                )

                print(
                    "body 전체 추출"
                )

            print(
                "글자수:",
                len(detail_text)
            )

            results.append(
                {
                    "title": job["title"],
                    "company": job["company"],
                    "url": job["url"],
                    "description": detail_text
                }
            )

        except Exception as e:

            print("ERROR:", e)

    browser.close()

with open(
    "jobs_detail.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        results,
        f,
        ensure_ascii=False,
        indent=2
    )

print("저장 완료")
print("공고 수:", len(results))