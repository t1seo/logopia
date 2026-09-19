# 구현 검증 — 2026-09-19

대상은 `d7d3cd4` 이후 현재 작업 트리입니다. [구현·관찰 보고서](../../research/icon-craft-2026/README.md), [실제 생성 실험](../../research/icon-craft-2026/experiment/README.md)과 함께 보세요. 테스트용 도형은 파일·상태·호출 경로 검증에만 사용했으며 디자인 품질 증거로 사용하지 않았습니다.

## 자동 검사

| 실행 | 결과 / 증거 |
| --- | --- |
| `uv run pytest -q --tb=short` | 마지막 보완 전 **1043 passed in 432.64s** — [전체 로그](pytest.txt) |
| 마지막 보완을 포함한 전체 재실행 | **1059 passed in 340.37s (0:05:40)** — [최종 로그](pytest-final.txt) |
| `uv run ruff check skills/logo-land/scripts integrations/hermes tests` | All checks passed |
| 같은 경로 `uv run ruff format --check` | 232 files already formatted |
| `uv run basedpyright` | 0 errors, 0 warnings, 0 notes |
| Hermes `basedpyright --pythonversion 3.11` | 0 errors, 0 warnings — [담당 검증](../../../integrations/hermes/CRAFT_QA.md) |
| 부모 배경 보존 회귀 | 실제 CLI에서 먼저 **2 failed, 1 passed** 확인. 수정 후 Asset/Prompt/Reference 관련 **24 passed** — [로그](background-regression.txt) |
| 최종 Hermes IP·입력 검증 보완 | 잘못된 기본값/입력 회귀를 먼저 실패로 확인한 뒤 **37 passed**. 전체 재실행에 포함합니다. |

부모 배경 회귀는 불투명 Brief에서 `import --background transparent`로 만든 Play 부모를 대상으로 했습니다. 수정 전 Prompt는 `requested_background="transparent"`인데 본문은 opaque였고, 자식 import는 `'opaque' == 'transparent'` 비교에서 실패했습니다. 수정 후 Prompt의 `Honor the requested transparent background`, 생략 시 자식 transparent, 명시적 opaque override와 부모 transparent 보존을 실제 CLI로 확인했습니다. 일반 로고 분기는 바꾸지 않았습니다.

기존 스타일 테스트는 제품 맥락 전달·미요청 팔레트/귀여움 제거라는 바뀐 계약만 갱신했습니다. 과거 Prompt와 PNG fixture 원본은 그대로 두고 [새 Prompt fixture](prompt-fixtures/README.md)를 분리했습니다. 최대 길이·스타일 격리·문자·색상 우선순위 검사는 유지했습니다. 수정/신규 Python 파일은 모두 250 nonblank/noncomment LOC 미만이며 가장 큰 변경 모듈 `host.py`는 236줄입니다. Reference 전달 로직은 별도 `host_references.py`에 있습니다.

## 실제 경로와 시각 QA

- ReferencePlan 6개를 모두 모델로 검증했고 실제 `init → reference-add → prompt --reference-plan` 18개 CLI 명령을 실행했습니다. 새 clone에 없는 캐시는 자동으로 확인한 것으로 처리하지 않습니다.
- [독립 QA](review-qa.md)는 실제 공개 CLI 27개, fixture provider를 쓴 Hermes 엔진 2개, 실제 브라우저 증거 열람 1개로 총 30개 시나리오를 확인했습니다. Positive/Negative·부모·ROI·누락/변조·stale revision·예산·alpha·선호 sidecar를 포함합니다.
- [Gallery 검증](../preference-review-2026-09-19.md)은 실제 브라우저의 1399px 및 390px 화면에서 원본 6개, 32/48/64/128 CSS px, light/dark, 세 Mask, 동일 48px 주변 후보와 세 블라인드 쌍을 확인했습니다. 실제 선호 선택·근거 입력·응답 저장은 하지 않았습니다.
- [스크린샷과 DOM·해시 기록](browser/)에는 정상 재촬영한 결과가 있습니다. 원본·일반 Gallery·블라인드 Gallery 총 18개 PNG의 전후 SHA-256이 동일합니다. 화면 효과는 진단 Simulation이며 OS 렌더링이 아닙니다.
- 실제 비교 실험은 **6회**, 후속 ‘틈’ 샘플은 **3회**로 합계 **9회, 수정 0회**, 한도 12회입니다. [비교 실험 호출 기록](../../research/icon-craft-2026/experiment/calls.json)과 [전체 예산](../../research/icon-craft-2026/call-budget.json)을 구분합니다. 이후 별도로 요청받은 [README 샘플 24개](../../showcase/2026-09-20-lifestyle/README.ko.md)는 해당 컬렉션의 호출 기록으로 추적합니다. 추가 과금 Provider를 연결하거나 실제 9개 탐색을 실행하지 않았습니다.
- 플랫폼 입력 검사와 PNG Handoff는 실제 CLI로 확인했습니다. Native Icon Composer/Xcode/Android package 및 Store 검증은 수행하지 않았습니다.

## 독립 검토

`omo:review-work`의 다섯 관점이 모두 **PASS**했습니다. Goal과 Code 검토가 찾은 부모 배경 상속 문제를 수정했고, 두 검토자가 실제 코드와 회귀 결과를 다시 확인했습니다. Security 검토는 파일·HTML·개인 Reference 처리에서 차단 문제를 찾지 못했습니다. QA는 위 30개 시나리오를 PASS했습니다. Context 검토는 실제 읽히는 IP 지침·최종 프롬프트·공개 안내의 남은 모순을 수정한 뒤 다시 확인했습니다. [Context 최종 기록](review-context.md)

초기 동시 구현 중의 테스트 실패는 최종 통과 근거로 사용하지 않았습니다. 별도 Hermes 전체 실행에서 일회성 `pid_listing` 프로세스 조회 실패 1개가 있었고 해당 테스트의 단독 재실행은 통과했습니다. 원인을 단정하거나 테스트를 무시하지 않았으며, 최신 전체 재실행을 최종 근거로 사용합니다.

디버깅용 instrumentation·환경 override·임시 journal은 남기지 않습니다. 이 검증 단계에는 유료 Provider 연결, 원격 Push, 배포, Release 발행을 포함하지 않았습니다. 사용자 선호·전 세계 고유성·실제 OS Appearance·모델별 개선 효과는 미검증입니다.
