# README sample refresh QA — 2026-09-20

새 원본 24개: 앱 아이콘 12개, 브랜드 로고 10개와 OFFCUT 레터링 2개입니다. 기존 README의 18개를 교체한 뒤, 추가 요청으로 색 배경 앱 아이콘 6개를 더 생성했습니다.

## 실제 실행과 검증

- 네이티브 이미지 생성 24회, 반환 24개. 재전송·수정 호출·별도 이미지 리뷰 모델 호출은 0회입니다. 프롬프트, 반환 파일명, 해시와 호출 이력은 각 source 및 [ledger](../call-ledger.json)에 기록했습니다. Provider는 네이티브 이미지 도구이며 모델 식별자는 노출되지 않았습니다.
- 현재 helper의 Brief 검증과 init/prompt/import 경로를 24개에 실행했습니다. `compare-gallery`로 실제 원본·최종 프롬프트 24쌍을 묶었습니다. 모델 호출은 helper가 아닌 네이티브 도구가 실행했습니다.
- [파일 검사](artifacts.json): PNG 디코딩, 1254×1254 크기, 불투명도, 이미지·프롬프트 해시, 원본 복사 일치, 양언어 README의 24개 새 이미지와 로컬 링크를 검사했습니다.
- [브라우저 검사](browser.json): 설치된 Google Chrome153.0.8010.52를 Playwright로 실제 실행했습니다. 원본 링크 24개를 각각 클릭했고, 모바일390px에서 가로 넘침이 없었습니다. 앱 아이콘12개 × 주변 배경2개 × 크기4개 =96개 표시 크기, CSS 마스크48개와 동일 조건의12개 앱 목록을 확인했습니다.
- 원본24개를 직접 시각적으로 확인했습니다. 앱 아이콘은32/48/64/128px, 브랜드 원본은240px 너비에서 추가로 보았습니다. [맥락 화면](peer-context.png) · [브랜드240px](lettering.png) · [모바일](gallery-mobile.png).
- 기존 보호 파일235개 중 이미지·소스 등233개는 바이트가 같고, 브랜드 안내 README2개는 현재 샘플 링크만 바꿨습니다. Logopia 헤더의 SHA256은 `4f8119477b7d8673ebfbb86d4d3255db28d8843c4522ea5e838f69784835471c`로 유지됐습니다.
- `git diff --check` 통과. 이번 추가 작업은 정적 PNG·문서·생성된 갤러리이며 제품 Python/TypeScript 코드는 수정하지 않았습니다. 기존 전체 테스트 결과를 이번 작업에서 재실행한 것으로 표시하지 않습니다.
- 읽기 전용 독립 검토에서24개 인벤토리·원본/프롬프트 해시·호출 수가 일치했습니다. 남아 있던 전체 흰 배경 설명4곳은 색6개/흰6개 구성으로 바로잡았습니다.

첫 브라우저 확인의 스크린샷 선택자 오류는 [QA 실행 기록](qa-attempts.json)에 남겼습니다. 숫자로 시작하는 HTML ID를 속성 선택자로 조회하도록 검사 스크립트를 고친 뒤 전체 확인이 통과했습니다. 제품 이미지나 HTML을 그 오류 때문에 변경하지 않았습니다.

## 관찰과 한계

설계 의도는 `design-spec.json`, 실제 관찰은 `visual-review.json`에 분리했습니다. 파일·링크 검사 통과를 미적 품질이나 사용자 승인으로 기록하지 않았습니다. 새24개에 대한 사용자 선택은 아직 없으며, 이전 SEAM Candidate2/5는 사용자가 거절했습니다.

작은 크기에서 빵의 세 갈래, 레코드와 슬리브, 밤/틈의 음절 구조, 캐릭터의 큰 표정 영역이 남습니다. 다만 Flow는 요청한 열린 입구 대신 닫힌 Counter로 나왔고, Daybreak에는 요청과 다른 흰 경계가 있습니다. Bun Club은 설계한 절제된 조형보다 사진 같은 질감이 강하며, Sprout은 정확한 픽셀 격자로 검증된 스프라이트가 아닙니다. Side B의 원형 CSS 미리보기는 슬리브 아래 바깥 모서리를 조금 잘라냅니다. 각 원본의 추가 한계도 관찰 파일에 명시했습니다.

원본 PNG에 색 보정·배경 교체·크롭을 하지 않았습니다. board.png와 QA 이미지는 브라우저 스크린샷입니다. 마스크·앱 목록·밝고 어두운 주변은 진단 시뮬레이션이며 실제 OS 렌더링, 플랫폼 승인 또는 Native Layered/Adaptive 패키지가 아닙니다. 사용자 스크린샷3장은 ignore된 개인 캐시에 있으며 공개 폴더에 복제하지 않았습니다.

## 실제 사용 경로

로컬에서 `index.html`을 열면 앱 아이콘12개가 먼저 나옵니다. 카드를 누르면 원본 PNG가 열리고, `diagnostics.html`에서 크기·주변·마스크를 비교할 수 있습니다.

```sh
uv run --locked python skills/logo-land/scripts/logo_project.py compare-gallery \
  --selection-file docs/showcase/2026-09-20-lifestyle/comparison-selection-24.json \
  --output docs/showcase/2026-09-20-lifestyle/comparison-copy
```

이 명령은 로컬에 새 helper 세션들이 보존되어 있을 때 새 비교 폴더를 만듭니다. 배포된 정적 폴더의 HTML과 PNG는 helper 세션 없이도 열 수 있습니다. 이미지 생성이나 추가 과금 Provider 연결을 실행하는 명령은 아닙니다.
