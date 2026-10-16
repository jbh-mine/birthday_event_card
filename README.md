# 당신의 마흔 번째 계절

타이포그래피, 색, 빛과 인터랙션으로 구성한 마흔 번째 생일 편지 사이트입니다.

## 바로 보기

GitHub Pages: https://jbh-mine.github.io/birthday_event_card/

## 구성

- 마흔 번째 계절을 여는 인트로
- 클릭해서 하나씩 읽는 사랑의 이유 40개
- 카드마다 등장하는 플레이모빌·애니메이션 캐릭터 일러스트
- 카드 사이에 나타나는 고양이 사진과 가끔 들리는 작은 고양이 소리
- 사진 없이 만든 아기·어린 시절·청춘·마흔·미래의 1분 성장 드라마와 오리지널 배경음
- 앞으로 함께할 시간을 그린 미래 편지
- 봉인을 눌러 여는 마지막 생일 편지
- 모바일·키보드·모션 감소 환경 지원

## 실행

Node.js 22.13 이상이 필요합니다.

이 PC에서는 프로젝트 폴더의 `생일편지_열기.cmd`를 더블클릭하면 기본 브라우저에서 바로 열립니다. 감상을 마친 후 `생일편지_종료.cmd`를 더블클릭하면 로컬 서버가 종료됩니다.

```bash
npm install
npm run dev
npm test
```

`npm run dev`, `npm run build`, `npm run start`는 Windows, macOS와 Linux에서 동일하게 동작합니다.

## GitHub Pages 배포

저장소의 **Settings → Pages → Build and deployment → Source**를 **GitHub Actions**로 설정합니다. 사이트가 생성되어 있지 않으면 빌드가 성공해도 `Configure GitHub Pages` 단계에서 404로 실패합니다.

`main`에 업로드하면 자동으로 테스트, 빌드, 정적 파일 내보내기와 배포가 진행됩니다. 수동 배포는 **Actions → Deploy birthday card to GitHub Pages → Run workflow**에서 실행합니다.

공유 링크와 미리보기 이미지는 공개 GitHub Pages 주소를 사용합니다. 다른 주소로 배포할 때는 `NEXT_PUBLIC_SITE_URL`에 사이트 경로까지 포함한 URL을 지정하세요.

마이크는 HTTPS 또는 localhost에서 사용할 수 있습니다. 권한을 허용하지 않거나 바람 감지가 어려워도 불꽃을 직접 눌러 영화와 마지막 편지로 진행할 수 있습니다. 영화는 재생 후 자막 메뉴에서 한국어 자막을 켤 수 있습니다.
