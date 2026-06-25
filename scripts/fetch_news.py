"""
네이버 뉴스 검색 오픈API를 호출해서 keywords.txt에 적힌 검색어별로
최신 뉴스 제목을 가져와 data/news.json 파일로 저장하는 스크립트입니다.

필요한 환경변수:
  NAVER_CLIENT_ID      - 네이버 개발자센터에서 발급받은 Client ID
  NAVER_CLIENT_SECRET  - 네이버 개발자센터에서 발급받은 Client Secret

GitHub Actions에서 이 스크립트를 실행하면, 그 결과로 data/news.json이
갱신되고, 워크플로우가 그 변경 사항을 저장소에 커밋합니다.
"""

import html
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone, timedelta

NAVER_NEWS_API_URL = "https://openapi.naver.com/v1/search/news.json"
DISPLAY_PER_KEYWORD = 10  # 검색어 하나당 가져올 기사 수 (최대 100)
KST = timezone(timedelta(hours=9))


def load_keywords(path: str) -> list[str]:
    keywords = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            keywords.append(line)
    return keywords


def clean_text(raw: str) -> str:
    """네이버 API가 응답에 섞어 보내는 <b> 태그와 HTML 엔티티를 제거합니다."""
    no_tags = re.sub(r"<.*?>", "", raw)
    return html.unescape(no_tags).strip()


def fetch_for_keyword(keyword: str, client_id: str, client_secret: str) -> list[dict]:
    params = {
        "query": keyword,
        "display": DISPLAY_PER_KEYWORD,
        "sort": "date",  # 최신순. 정확도순을 원하면 "sim"으로 변경하세요.
    }
    url = f"{NAVER_NEWS_API_URL}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url)
    req.add_header("X-Naver-Client-Id", client_id)
    req.add_header("X-Naver-Client-Secret", client_secret)

    with urllib.request.urlopen(req, timeout=10) as resp:
        body = json.loads(resp.read().decode("utf-8"))

    items = []
    for item in body.get("items", []):
        items.append(
            {
                "title": clean_text(item.get("title", "")),
                "description": clean_text(item.get("description", "")),
                "link": item.get("originallink") or item.get("link"),
                "naver_link": item.get("link"),
                "pub_date": item.get("pubDate"),
            }
        )
    return items


def main() -> None:
    client_id = os.environ.get("NAVER_CLIENT_ID")
    client_secret = os.environ.get("NAVER_CLIENT_SECRET")

    if not client_id or not client_secret:
        print(
            "오류: NAVER_CLIENT_ID / NAVER_CLIENT_SECRET 환경변수가 설정되어 있지 않습니다.",
            file=sys.stderr,
        )
        sys.exit(1)

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    keywords = load_keywords(os.path.join(base_dir, "keywords.txt"))

    categories = []
    for keyword in keywords:
        try:
            items = fetch_for_keyword(keyword, client_id, client_secret)
            categories.append({"keyword": keyword, "items": items})
            print(f"[OK] '{keyword}' - {len(items)}건 수집")
        except Exception as exc:  # 한 키워드가 실패해도 나머지는 계속 진행
            print(f"[FAIL] '{keyword}' - {exc}", file=sys.stderr)
            categories.append({"keyword": keyword, "items": [], "error": str(exc)})

    output = {
        "updated_at": datetime.now(KST).isoformat(),
        "categories": categories,
    }

    out_path = os.path.join(base_dir, "data", "news.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n저장 완료: {out_path}")


if __name__ == "__main__":
    main()
