from playwright.sync_api import sync_playwright
import json

SEARCH_WORD = "AI Engineer"

jobs = []

with sync_playwright() as p:

    browser = p.chromium.launch(headless=False)

    page = browser.new_page()

    page.goto(
        f"https://www.saramin.co.kr/zf_user/search?searchword={SEARCH_WORD}"
    )

    page.wait_for_timeout(5000)

    postings = page.locator("div.item_recruit")

    count = postings.count()

    print("공고 수:", count)

    for i in range(min(count, 30)):

        try:
            item = postings.nth(i)

            title = item.locator("h2 a").inner_text()

            href = item.locator("h2 a").get_attribute("href")

            company = item.locator(".corp_name").inner_text()

            url = "https://www.saramin.co.kr" + href

            jobs.append(
                {
                    "title": title,
                    "company": company,
                    "url": url
                }
            )

        except Exception as e:
            print(e)

    browser.close()

with open(
    "jobs.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        jobs,
        f,
        ensure_ascii=False,
        indent=4
    )

print("저장 완료:", len(jobs))