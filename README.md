# 네이버 뉴스 자동 수집기

네이버 뉴스 검색 오픈API로 정해진 검색어들의 최신 뉴스 제목을 **매시간(또는 매일) 자동으로**
가져와서, 깔끔한 웹페이지로 보여주는 무료 자동화 앱입니다.

- 서버를 직접 운영하지 않습니다. **GitHub Actions**(무료, 정해진 시간에 코드를 실행해주는 서비스)가
  주기적으로 네이버 API를 호출하고, 그 결과를 이 저장소의 `data/news.json` 파일에 저장합니다.
- **GitHub Pages**(무료 웹호스팅)가 `index.html`을 인터넷에 공개해서, 누구나 그 주소로 접속해
  최신 뉴스를 볼 수 있습니다.
- 둘 다 GitHub 무료 계정만 있으면 비용이 들지 않습니다.

---

## 0. 준비물

- GitHub 계정 (없으면 https://github.com 에서 무료 가입)
- 네이버 계정

---

## 1. 네이버 오픈API 키 발급받기

1. https://developers.naver.com 접속 후 로그인
2. 상단 메뉴에서 **Application → 애플리케이션 등록** 클릭
3. 애플리케이션 이름은 자유롭게 입력 (예: `naver-news-app`)
4. "사용 API"에서 **검색** 선택
5. 비로그인 오픈 API 서비스 환경에서 **WEB 설정**을 추가하고, 웹 서비스 URL은
   아래 3단계에서 만들 GitHub Pages 주소(`https://본인아이디.github.io/저장소이름/`)를
   입력 (정확한 주소를 몰라도 임시로 `https://github.com` 등을 넣고 나중에 수정해도 됩니다)
6. 등록 완료 후 발급되는 **Client ID**와 **Client Secret**을 복사해 둡니다.
   (Client Secret은 "보기" 버튼을 눌러야 보입니다)

이 API는 하루 25,000회까지 무료로 호출할 수 있어서, 키워드 몇 개를 매시간 수집해도
한도에 걸릴 일은 거의 없습니다.

---

## 2. GitHub 저장소 만들고 파일 올리기

1. GitHub에서 **New repository** 클릭 → 이름 입력 (예: `naver-news-app`) → **Public**으로 설정
   (GitHub Pages를 무료로 쓰려면 Public이어야 합니다) → Create
2. 방금 만든 저장소 페이지에서 **Add file → Upload files**를 클릭하고,
   이 폴더 안의 모든 파일/폴더(`.github`, `scripts`, `data`, `keywords.txt`, `index.html`, `README.md`)를
   통째로 드래그해서 올립니다.
   - 폴더 구조가 그대로 유지되어야 합니다 (`.github/workflows/update-news.yml` 경로가 깨지지 않게 주의)
   - 익숙하다면 `git clone` 후 `git add . && git commit && git push`로 올려도 됩니다.

---

## 3. API 키를 GitHub에 안전하게 등록하기 (Secrets)

API 키를 코드에 직접 적지 않고, GitHub의 "비밀 변수" 기능에 등록해서 사용합니다.

1. 저장소 페이지에서 **Settings → Secrets and variables → Actions** 이동
2. **New repository secret** 클릭 → 이름 `NAVER_CLIENT_ID`, 값에 1단계에서 받은 Client ID 입력 → Add secret
3. 같은 방법으로 이름 `NAVER_CLIENT_SECRET`, 값에 Client Secret 입력 → Add secret

---

## 4. 검색 키워드 설정하기

`keywords.txt` 파일을 열어서 원하는 검색어를 한 줄에 하나씩 적으세요.
기본값은 아래와 같습니다.

```
경제
AI
부동산
```

GitHub 웹사이트에서 바로 이 파일을 클릭 → 연필(✏️) 아이콘으로 수정 → **Commit changes**로
저장할 수 있습니다.

---

## 5. GitHub Pages로 웹페이지 공개하기

1. 저장소 **Settings → Pages** 이동
2. **Source**를 `Deploy from a branch`로, **Branch**는 `main` / `(root)`로 선택 → Save
3. 1~2분 후 페이지 상단에 표시되는 주소(`https://본인아이디.github.io/저장소이름/`)로 접속하면 화면을 볼 수 있습니다.
   (처음엔 "아직 수집된 뉴스가 없습니다" 화면이 보이는 게 정상입니다 — 6단계 진행하면 채워집니다)

---

## 6. 첫 자동 수집 실행해보기

1. 저장소 **Actions** 탭 이동
2. 왼쪽에서 **Update Naver News** 워크플로우 선택
3. **Run workflow** 버튼 클릭해서 수동으로 한 번 실행
4. 1분 정도 후 초록색 체크가 뜨면 성공. `data/news.json`이 갱신되고,
   잠시 후 5단계의 웹페이지를 새로고침하면 뉴스가 보입니다.

이후로는 워크플로우가 **매시간 자동으로** 같은 작업을 실행합니다. 사람이 따로 손댈 필요가 없습니다.

---

## 갱신 주기 바꾸기 (매시간 → 매일 등)

`.github/workflows/update-news.yml` 파일의 `cron` 값을 수정하면 됩니다.
GitHub Actions의 cron 시간은 **UTC 기준**이라, 한국시간(KST = UTC+9)으로 바꿔서 계산해야 합니다.

| 원하는 주기 | cron 값 | 의미 |
|---|---|---|
| 매시간 정각 | `0 * * * *` | 기본값 |
| 하루 한 번, 한국시간 오전 7시 | `0 22 * * *` | UTC 22:00 = 다음날 KST 07:00 |
| 하루 한 번, 한국시간 오후 6시 | `0 9 * * *` | UTC 09:00 = KST 18:00 |
| 6시간마다 | `0 */6 * * *` | 하루 4번 |

수정 후 커밋하면 다음 스케줄부터 바로 적용됩니다.

---

## 자주 묻는 질문

**Q. 비용이 드나요?**
공개(Public) 저장소 기준으로 GitHub Actions, GitHub Pages, 네이버 오픈API 모두 무료 한도 안에서
사용하므로 비용이 들지 않습니다.

**Q. 워크플로우가 빨간 X로 실패해요.**
Actions 탭에서 실패한 실행을 클릭하면 로그가 보입니다. 대부분 `NAVER_CLIENT_ID` /
`NAVER_CLIENT_SECRET` Secret 이름을 잘못 입력했거나, 네이버 애플리케이션에서 "검색" API를
선택하지 않은 경우입니다.

**Q. 키워드를 더 추가해도 되나요?**
네, `keywords.txt`에 줄을 추가하면 됩니다. 키워드 수가 많아질수록 API 호출 수가 늘어나니
(키워드 1개 = 1회 호출) 너무 많이 추가하지만 않으면 됩니다.

**Q. 휴대폰 앱처럼 쓰고 싶어요.**
모바일 브라우저에서 GitHub Pages 주소를 열고 "홈 화면에 추가"를 하면 앱처럼 아이콘으로
추가해서 쓸 수 있습니다.
