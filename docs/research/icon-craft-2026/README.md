# Logopia 조형·비교 개선 — 2026-09-19

> **2026-09-20 사용자 피드백:** 아래 SEAM 실험의 Candidate2(a2)와 Candidate5(b2)는 형태와 색상 모두 부적합하다는 평가를 받았습니다. [피드백 기록](user-feedback-2026-09-20.json). 이 실험을 사용자 선호 개선의 증거로 취급하지 않습니다. [새 README 샘플 24개](../../showcase/2026-09-20-lifestyle/README.ko.md)는 별도 작업이며 아직 선택받지 않았습니다.

기존 `d7d3cd4`의 아이콘 품질 개선과 Hermes Pipeline 위에 구현했습니다. 기존 PNG·저장 프롬프트·Session을 다시 만들거나 덮어쓰지 않았습니다. 이번 변경의 핵심은 **선택한 Reference의 관찰 → 구체적인 형태 결정 → 실제 생성 입력 → 같은 조건의 비교**를 연결하는 것입니다.

- [방법을 가린 실제 3쌍 비교](experiment/blind/index.html): 폴더를 내려받아 브라우저에서 여세요. 아직 사용자 선택은 없습니다.
- [원본 6개·정확한 프롬프트](experiment/gallery/index.html), [실험 조건과 관찰](experiment/README.md), [호출 기록](experiment/calls.json)
- [공식 자료 근거](sources.md), [Reference manifest](references.json), [실행 가능한 ReferencePlan 6개](reference-plans/README.md)
- [실제 브라우저 검증](../../qa/preference-review-2026-09-19.md), [독립 CLI QA 30개 시나리오](../../qa/icon-craft-2026/review-qa.md)
- 후속 샘플 요청: [산책·휴식 앱 ‘틈’의 새 원본 3개](teum-samples/README.md). SEAM 6회와 합쳐 실제 생성 9회이며, [전체 예산](call-budget.json)에서 별도로 추적합니다.

## A. 기존 이미지에서 직접 관찰한 것

원본과 해당 최종 프롬프트를 함께 열었습니다. [32/48/64/128px 진단 시트](existing-size-check.png)는 별도 파일이며 원본을 바꾸지 않습니다. 앱 아이콘 5개와 일반 로고·Lettering 2개를 봤습니다. 아래 위치는 이미지 내부 위치입니다.

| 원본 / 해당 프롬프트 | 직접 관찰 | 해석과 한계 |
| --- | --- | --- |
| [Abstract](../../app-icons-quality-v1/images/abstract-quality-v1.png) / [prompt](../../app-icons-quality-v1/prompts/abstract-quality-v1.txt) | 아래쪽 중앙의 파란 둥근 끝과 산호색 띠 사이에 가늘게 좁아지는 틈이 있습니다. 다른 끝은 넓고 둥급니다. 32px에서는 그 접점 차이가 약해지고 두 고리가 주로 남습니다. | 틈을 식별 특징으로 삼으려면 폭을 더 분명히 결정할 필요가 있습니다. 반복 고리와 혼동할 위험이지, 전 세계 유사성 판정은 아닙니다. |
| [Soft 3D](../../app-icons-quality-v1/images/soft-3d-quality-v1.png) / [prompt](../../app-icons-quality-v1/prompts/soft-3d-quality-v1.txt) | 양쪽 상단 둥근 엽과 아래 뾰족점, 중앙 능선이 보입니다. 큰 원본의 표면에는 잔점 질감이 있고 32px에서 능선보다 두 엽의 윤곽이 우선합니다. | 잎보다 하트로 읽힐 수 있습니다. 프롬프트의 매끈한 표면·기공 배제 요구를 결과가 완전히 따르지 않았습니다. |
| [Monogram 모](../../app-icons-quality-v1/images/monogram-quality-v1.png) / [prompt](../../app-icons-quality-v1/prompts/monogram-quality-v1.txt) | `모`가 읽히고 상단 Counter가 열려 있습니다. 위 사각 Counter의 곡률과 아래 가로획의 둥근 끝은 서로 다릅니다. 32px에서도 음절 구조가 남습니다. | 글자 오염으로 실패 처리하지 않습니다. 곡률과 획 무게는 추가 광학 조정의 대상입니다. |
| [Pictogram](../../app-icons-quality-v1/images/pictogram-quality-v1.png) / [prompt](../../app-icons-quality-v1/prompts/pictogram-quality-v1.txt) | 구름 왼쪽 위의 해와 구름 사이 파란 틈이 아래로 갈수록 좁아집니다. 원본에는 미세한 면 명암이 있고 32px에서는 해·구름이라는 두 덩어리가 남습니다. | 날씨 의미는 읽히지만 특정 제품을 구별할 구조는 약할 수 있습니다. 기본 날씨 Glyph와의 혼동은 비교할 가설입니다. |
| [IP owl](../../app-icons/images/ip-a1.png) / [prompt](../../app-icons/prompts/ip-a1.txt) | 얼굴 아래에 책·양쪽 날개·발·여러 작은 깃털선이 있습니다. 32px에서는 책의 접힘과 날개선이 줄어들며 큰 얼굴과 눈이 우선합니다. | 캐릭터 자체를 배제할 이유는 없습니다. 독서라는 설명보다 작은 크기의 큰 얼굴에 의존한다는 관찰입니다. |
| [LUMA](../../showcase/2026-09-white/images/01-luma.png) / [실제 a-v2 최종 prompt](../../showcase/2026-09-white/sources/01-luma/revisions/a-v2/prompt.txt) | 정확한 대문자 LUMA, 넓은 M의 V형 골과 다색 글자가 보입니다. L/U 사이가 M/A 사이보다 좁게 보입니다. | 원래 용도는 240px 브랜드 표시입니다. 32px 정사각에 작게 보인다는 이유로 Wordmark를 실패 처리하지 않습니다. 기존 M 수정 계보도 보존했습니다. |
| [고요](../../showcase/2026-09-white/images/03-goyo.png) / [prompt](../../showcase/2026-09-white/sources/03-goyo/prompt.txt) | 이름은 정확합니다. 위 두 곡선의 끝은 뾰족하고 아래 글자 획은 더 균일합니다. 32px에서는 상단 심볼의 대비가 먼저 남습니다. | 입술 같은 연상은 해석입니다. 심볼과 Typography의 곡률 관계를 검토할 수 있으나 한글 오류로 취급하지 않습니다. |

## B. 코드에서 확인하고 수정한 원인

| 확인한 구조 | 실제 변경 |
| --- | --- |
| 아이콘 Builder가 Brief의 제품·사용 맥락·필수 제외 조건을 전달하지 않았고, IP에 고정 귀여움·색상 조합이 있었습니다. | `app_icon_prompts.py`에 필요한 Brief만 전달하고 기본 팔레트·표정·비례 강제를 제거했습니다. Hermes의 실제 최종 IP 프롬프트와 읽히는 지침도 함께 수정했습니다. 사용자 색·문자·배치는 우선합니다. |
| 기존 Reference 저장은 색 분석 중심이며 URL만으로 생성 이미지 입력이 되지 않았습니다. | `conditioning_models.py` / `conditioning.py`가 이미지 해시·관찰·positive/negative·ROI·부모를 검증하고 실제 도구 인자를 만듭니다. `prompt --reference-plan`으로 연결했습니다. Negative는 회피 특성만 전달하며 이미지 입력에서 제외합니다. |
| 모든 아이콘에 불투명 평면 타일 정책을 적용했습니다. | `asset_*` 모듈과 Import/Export를 통해 concept, Apple/Android authored layer, Play listing을 구분했습니다. 전경 alpha를 허용하고 배경·크기·안전영역을 별도로 검사합니다. 부모 배경 상속 회귀도 수정했습니다. |
| 후보 비교가 생성 방법·자체 설명과 함께 노출되고 선호 기록 경로가 없었습니다. | 기존 Gallery에 48px·같은 크기 주변 후보를 추가했습니다. 별도 `preference-*` 경로는 방법을 숨기고 A/B/비슷함/둘 다 부적합과 관찰을 저장합니다. QA·AI 추천·사용자 선택을 합치지 않습니다. |
| Hermes의 후보 수와 방향 수, 후보 상한·실제 LLM 호출 예산이 묶여 있었습니다. | 방향×후보 슬롯, 바뀐 변수, Reference와 실제 Prompt·Provider·부모를 저장합니다. 기본 3회/IP 6회는 유지하고 선택적 3×3, 최대 수정 2회와 검토 예산을 함께 검증합니다. 알 수 없는 이미지 결과는 자동 재전송하지 않습니다. |

각 코드 변경이 과거 이미지의 특정 결함을 유일하게 일으켰다고 주장하지 않습니다. 이미지 모델의 실행 변동성도 있습니다.

## C. 실험으로 확인할 가설과 이번 결과

넓은 Counter·접점, 일관된 곡률과 제한된 색 역할이 작은 크기의 식별에 도움이 될 가능성을 탐색했습니다. 실제 SEAM 3대3에서는 내부 글줄 제거, 열린 틈, 산호색 접힌 끝이 관찰됩니다. 반면 파일 모양의 상투성, 입체 표면 질감은 남았습니다. **사용자 선호 개선, 설치 전환율, 각 개선 요소의 독립 효과는 미검증**입니다. [실험 상세](experiment/README.md)

## 채택한 원칙과 채택하지 않은 유행

Things의 핵심 형태 유지, Craft의 곡률·간격, Linear의 Mark/Wordmark/Icon 역할 구분, Gentler Streak의 유기적 윤곽, Figma의 공통 부품 규칙, Not Boring의 제품과 맞는 단일 오브젝트를 서로 다른 선택지로 사용합니다. Glass·Gradient·3D·흑백 Minimalism을 공통 정답으로 삼지 않습니다. LogoLounge의 첫 글자·기울기·부피감은 Lettering 탐색 변수이며 필수 Enum이 아닙니다. 발표 시점·출시 여부·관찰과 해석·권리 확인 상태는 [출처 기록](sources.md)과 Manifest에 남겼습니다.

## 실제 사용 경로와 호환성

```sh
# 이 작업에서 만든 실제 세션의 읽기 전용 진단
uv run --locked python skills/logo-land/scripts/logo_project.py \
  asset-check --session seam-craft-2026 --artifact b3

# 출력 경로는 새 경로여야 합니다. 저장된 명시적 revision/원본을 비교합니다.
uv run --locked python skills/logo-land/scripts/logo_project.py \
  preference-gallery \
  --selection-file docs/research/icon-craft-2026/experiment/blind-selection.json \
  --output output/seam-preference-review
```

새 작업의 Reference 입력은 [실행 예제](reference-plans/README.md), 결과 선택은 [Preference 안내](../../preference-review.md), Asset JSON은 [플랫폼 안내](../../icon-assets.md), Hermes 3×3 요청은 [실제 CLI·도구 계약](../../../integrations/hermes/CONTRACT.md)을 따릅니다. 위 Session은 이 작업 공간의 로컬 기록이며 새 clone에는 포함되지 않습니다. 공개 HTML과 원본은 Session 없이 열립니다.

기존 Session·Reference 없는 Prompt·일반 로고·게임 타이틀·정확한 한글·기존 ZIP 전달을 유지합니다. 새 필드는 선택 사항이며 예전 Prompt 파일을 다시 쓰지 않습니다. Codex는 실제 복수 이미지 인자를 지원하고, 현재 Hermes는 계획·검토에 Reference 픽셀을 보지만 생성에는 분석 텍스트를 전달합니다. Hermes의 단일 `image_url`은 실제 편집 부모용입니다.

Native Icon Composer/Xcode 문서, Android Adaptive package, 실제 OS Appearance 렌더링과 Store 심사 통과는 만들거나 검증하지 않았습니다. PNG Handoff와 진단 결과를 제공하며 `native_package=false`, `platform_validation=not_run`을 유지합니다. 이 리서치·실험 단계에는 유료 Provider 연결·Push·배포·Release를 포함하지 않았습니다.

검사 결과와 검토 판정은 [최종 검증 기록](../../qa/icon-craft-2026/README.md)에 있습니다.
