# Logopia에 보완할 로고·브랜드 스킬과 플러그인 조사

조사일: 2026-10-01. 공개 원문·공식 문서와 현재 세션의 설치/연결 가능 상태를 확인했습니다. 후보 스킬 설치, 외부 계정 연결, 이미지 생성 API 호출은 실행하지 않았습니다. 아래 평가는 기능과 프로젝트 적합성에 대한 판단이며, 실제 생성물의 품질 비교는 아닙니다.

**추천은 브랜드 전략에 `brand-building-skills`, 브랜드 응용 시안에 `brandkit`, 벡터 제작에 Recraft 공식 원격 MCP입니다.** Figma는 편집 가능한 가이드와 협업 파일을 만들 때 보조 후보입니다. 여러 로고 생성 스킬을 한꺼번에 추가하는 것보다 현재 Logopia가 제공하지 않는 결과물을 보완하는 편이 효과적입니다.

스킬은 에이전트의 작업 지침과 절차를 제공하고, MCP·앱 연결은 외부 서비스의 실제 기능을 제공합니다. 스킬이 SVG를 언급한다고 벡터 생성 모델이나 변환 서비스가 함께 제공되는 것은 아닙니다.

## 현재 Logopia와 겹치는 부분

Logopia는 이미 브리프, 여러 디자인 방향, 네이티브 이미지 생성, 소형 가독성·정확한 글자·투명도·팔레트 검토, 수정 이력, PNG·ZIP·짧은 브랜드 가이드를 지원합니다. 결과는 래스터 PNG이며 SVG/EPS/AI, 편집 가능한 벡터 경로와 폰트 파일은 별도 작업입니다. 따라서 **브랜드 전략, 실제 벡터, 브랜드 응용물**이 주요 보완점입니다. [프로젝트 README](../../README.md), [Logo Land 스킬](../../skills/logo-land/SKILL.md)

`ip-as-logo`는 s1dashu 원본을 MIT 크레딧과 함께 이미 반영했습니다. 현재 세션에는 Hail Mary의 `minimal-logo`·`ip-as-logo`, `better-colors`, `leonardo-colors`, `google-fonts`, `studio-design-system`도 있습니다. 이들은 신규 발견으로 계산하지 않았습니다. 특히 `leonardo-colors`는 Adobe Leonardo의 대비 기반 색상 라이브러리이며 Leonardo.ai 이미지 생성 서비스가 아닙니다. [기존 적응 기록](../../skills/logo-land/references/ip-mascot.md), [서드파티 고지](../../THIRD_PARTY_NOTICES.md)

## 외부 스킬 후보

| 후보 | 실제로 제공하는 것 | Logopia 활용 판단 | 의존성·제한 |
| --- | --- | --- | --- |
| **Brand Building Skills / brand-identity** | 브랜드 전략을 로고 방향·팔레트·타입·이미지·응용물 브리프로 정리 | **우선 도입 후보.** 로고 생성 전 전략 계층 보완 | 문서 중심. 자체 이미지·벡터 생성 없음 |
| **Taste Skill / brandkit** | 로고와 색상·타입·목업을 묶은 브랜드 보드 이미지 프롬프트 | **우선 참고 후보.** 최종 로고의 브랜드 응용 시안 | 기본 산출물은 한 장의 이미지. 개별 SVG·템플릿·토큰 팩 아님 |
| **ReScienceLab / logo-creator** | Gemini 이미지 생성→여러 안→배경 제거→Recraft SVG 변환 | 전체 작업 흐름 참고용. 기존 기능과 중복이 큼 | 추가 스킬, API 키 3종, 서비스별 사용량 비용. 코드 검토 필요 |
| **rknall / SVG Logo Designer** | 에이전트가 직접 SVG 코드와 레이아웃 변형을 작성하는 지침 | 벡터 작업 설계 참고. 현재 상태 그대로의 도입 우선순위는 낮음 | 라이선스 확인 불가, 작은 저장소, 폰트·렌더 검증 보완 필요 |

### 1. Brand Building Skills

`brand-identity`는 기존 `.agents/brand-context.md`를 먼저 읽고, 브랜드 전략을 로고 방향·색상·타입·이미지·아이콘·디자인 원칙·응용물로 번역하는 8부 브리프를 만듭니다. 관련 `brand-strategy`, `brand-naming`, `brand-voice`, `brand-guidelines`도 같은 저장소에 있습니다. 문서형 Agent Skills이므로 Codex에 적용하기 쉬운 편입니다. [고정된 스킬 원문](https://github.com/arnabbagxd/Brand-building-skills/blob/4a0a8b5b7a0f64bf0fc551978a18a591670a5223/skills/brand-identity/SKILL.md), [저장소 설명](https://github.com/arnabbagxd/Brand-building-skills/blob/4a0a8b5b7a0f64bf0fc551978a18a591670a5223/README.md)

Logopia에는 `brand-context`와 `brand-identity`부터 좁게 적용하는 것이 좋습니다. `brand-strategy` 원문에는 인도 시장 중심 예시와 부족한 정보를 추론하라는 지침이 있으므로, 한국 프로젝트에는 시장·경쟁사 사실과 가정을 분리하고 기존 브리프를 재질문하지 않도록 조정해야 합니다. 자체 로고 이미지나 편집 가능한 벡터를 생성하는 도구는 아닙니다. [전략 스킬 원문](https://github.com/arnabbagxd/Brand-building-skills/blob/4a0a8b5b7a0f64bf0fc551978a18a591670a5223/skills/brand-strategy/SKILL.md)

라이선스는 MIT입니다. 조사 당시 `brand-identity` 설치 지표는 약 1.6K, 저장소는 GitHub API 기준 699 stars였습니다. [라이선스](https://github.com/arnabbagxd/Brand-building-skills/blob/4a0a8b5b7a0f64bf0fc551978a18a591670a5223/LICENSE), [설치 지표](https://www.skills.sh/arnabbagxd/brand-building-skills/brand-identity), [저장소 API](https://api.github.com/repos/arnabbagxd/Brand-building-skills)

```bash
# 설치 예시이며 이번 조사에서는 실행하지 않았습니다.
npx skills add arnabbagxd/brand-building-skills --skill brand-context --skill brand-identity --agent codex
```

### 2. Taste Skill / brandkit

브랜드의 의미와 시각적 은유를 정하고 로고, 구성 원리, 디지털 화면, 태그라인, 팔레트, 타입, 실물 목업, 이미지 방향을 하나의 보드로 구성합니다. 기본은 3×3, 4:3 또는 16:10의 브랜드 키트 이미지입니다. 특정 생성 API를 강제하지 않는 프롬프트 중심 스킬이어서 Codex의 이미지 생성 기능과 조합하기 좋습니다. [고정된 스킬 원문](https://github.com/Leonxlnx/taste-skill/blob/ce26fc25c0e5e8cab638f883de62d9a86ee5e45b/skills/brandkit/SKILL.md)

Logopia의 선택된 로고를 명함·패키지·웹 화면에서 어떻게 보일지 제시하는 단계에 참고할 만합니다. 다만 로고가 모든 패널에서 정확히 유지되는지, 텍스트가 맞는지는 별도 검토해야 합니다. 결과는 시각적 방향을 보여 주는 이미지이며, 개별 편집 파일이나 실제 사용 폰트·색상 토큰의 증거가 되지 않습니다.

라이선스는 MIT입니다. 설치 지표는 CLI 약 332.8K, 같은 날 리더보드 약 333.5K이며 저장소는 91,639 stars였습니다. 별 수는 전체 Taste Skill 저장소의 수치입니다. [라이선스](https://github.com/Leonxlnx/taste-skill/blob/ce26fc25c0e5e8cab638f883de62d9a86ee5e45b/LICENSE), [리더보드](https://www.skills.sh/), [저장소 API](https://api.github.com/repos/Leonxlnx/taste-skill)

```bash
npx skills add leonxlnx/taste-skill --skill brandkit --agent codex
```

### 3. ReScienceLab / logo-creator

스타일과 비율을 정하고 기본 20개 후보를 생성한 뒤 HTML에서 비교하고, 선택한 로고의 여백 자르기·배경 제거·SVG 변환까지 수행하는 흐름입니다. `nanobanana` 스킬과 `GEMINI_API_KEY`, `REMOVE_BG_API_KEY`, `RECRAFT_API_KEY`를 요구합니다. 따라서 스킬 자체 설치 비용과 외부 서비스 사용 비용을 구분해야 합니다. [고정된 스킬 원문](https://github.com/ReScienceLab/opc-skills/blob/f79569f1ee76dd3c217279b1b633f97709343423/skills/logo-creator/SKILL.md)

Codex에서 활용할 수 있는 Markdown과 스크립트로 구성되어 있으나 실행 호환성은 시험하지 않았습니다. 특히 `vectorize.py`는 환경변수에 키가 없으면 `~/.zshrc`에서 찾는 처리가 있습니다. 이 부분은 Logopia에 그대로 가져오지 않는 편이 좋습니다. 현재 기능과 생성·수정·미리보기 단계가 겹치므로, **전체 설치보다 SVG 전달 과정 참고**를 권합니다. 벡터 기능만 필요하다면 아래 Recraft 공식 원격 MCP가 더 직접적인 후보입니다. [벡터화 코드](https://github.com/ReScienceLab/opc-skills/blob/f79569f1ee76dd3c217279b1b633f97709343423/skills/logo-creator/scripts/vectorize.py)

라이선스는 Apache-2.0, 설치 약 3.0K, 저장소 1,846 stars입니다. skills.sh 페이지에는 조사 당시 외부 감사 Fail/Warn도 표시되었습니다. 이는 실행 검증 결과가 아니라 디렉터리의 표시이며, 위 원문 코드 확인과 함께 판단했습니다. [라이선스](https://github.com/ReScienceLab/opc-skills/blob/f79569f1ee76dd3c217279b1b633f97709343423/LICENSE), [설치·감사 표시](https://www.skills.sh/resciencelab/opc-skills/logo-creator), [저장소 API](https://api.github.com/repos/ReScienceLab/opc-skills)

```bash
# 참고용 명령입니다. 외부 서비스 연결과 코드 검토가 별도로 필요합니다.
npx skills add resciencelab/opc-skills --skill logo-creator --skill nanobanana --agent codex
```

### 4. rknall / SVG Logo Designer

로고 요구사항을 모으고 3~5개 콘셉트, 가로·세로·아이콘형 변형, 컬러·단색 버전을 SVG 코드로 작성하게 합니다. `viewBox`, 그룹, 접근성 설명, 경로 최적화 지침이 있어 단순 기하 심볼이나 레이아웃 구조 참고에 적합합니다. 별도 생성 API는 요구하지 않습니다. [고정된 원문](https://github.com/rknall/claude-skills/blob/ca7fbd0e07f824b119030f323da3409bc779f9bc/svg-logo-designer/SKILL.md)

다만 Claude의 `Write` 호출 예시를 Codex 파일 도구로 바꿔야 하고, 샘플 워드마크는 `<text>`와 시스템 폰트를 사용하므로 글자 형태가 확정된 벡터 아웃라인과 다릅니다. 결과가 실제로 제대로 렌더되는지와 작은 크기의 가독성도 별도 확인이 필요합니다. 조사한 커밋 트리에서 라이선스 파일을 찾지 못했고 GitHub API의 라이선스 값도 null이어서, **Logopia에 코드나 지침을 복제·재배포하는 후보로는 보류**합니다. [저장소 트리](https://github.com/rknall/claude-skills/tree/ca7fbd0e07f824b119030f323da3409bc779f9bc), [저장소 API](https://api.github.com/repos/rknall/claude-skills)

저장소는 80 stars입니다. 설치 수는 같은 날 CLI가 약 7.3K, 상세 페이지가 약 1.2K로 달랐습니다. 어느 수치가 정확한지 단정하지 않았고, 기능 적합성과 원문 품질을 우선했습니다. [상세 페이지](https://www.skills.sh/rknall/claude-skills/svg-logo-designer)

```bash
# 검색된 명령 형식 기록입니다. 현재 권장 설치 대상은 아닙니다.
npx skills add rknall/claude-skills --skill 'SVG Logo Designer' --agent codex
```

### 이름과 달리 이번 목적에 맞지 않는 후보

- **Anthropic `brand-guidelines`**: 새 브랜드를 개발하는 스킬이 아니라 Anthropic의 지정 색상·Poppins/Lora 타입을 산출물에 적용하는 스킬입니다. Apache-2.0이며 설치는 약 98.5K지만, Logopia의 신규 브랜드 제작 기능 보완에는 우선순위가 낮습니다. [고정 원문](https://github.com/anthropics/skills/blob/8a1541c4a3ffa5a20a5a91de0dcf3f0bab1d1ef4/skills/brand-guidelines/SKILL.md), [라이선스](https://github.com/anthropics/skills/blob/8a1541c4a3ffa5a20a5a91de0dcf3f0bab1d1ef4/skills/brand-guidelines/LICENSE.txt), [설치 지표](https://www.skills.sh/anthropics/skills/brand-guidelines)
- **Warp `brandalf`**: Warp·Oz 브랜드의 공식 가이드를 읽어 해당 브랜드의 산출물을 만드는 전용 스킬입니다. MIT, 저장소 598 stars, CLI 설치 약 26.6K였습니다. 범용 브랜드 제작 스킬로 추천하지 않습니다. [고정 원문](https://github.com/warpdotdev/common-skills/blob/69b4753651ab7fab518c82be087b9f1d5b966631/.agents/skills/brandalf/SKILL.md), [저장소](https://github.com/warpdotdev/common-skills)

## 외부 서비스·MCP 후보

| 후보 | 공식 문서상 기능 | Logopia에 추가되는 가치 | 현재 세션 상태 |
| --- | --- | --- | --- |
| **Recraft 공식 원격 MCP** | 텍스트→래스터·벡터, 래스터 벡터화, 부분 수정, 배경 제거, 커스텀 스타일 | 실제 벡터 파일 제작 경로 | 내장 플러그인 검색 결과는 없음. 외부 MCP 연결 후보이며 연결 미시험 |
| **Figma** | Codex에서 네이티브 프레임·컴포넌트·변수·Auto Layout 작성 | 편집 가능한 브랜드 가이드·디자인 토큰·협업 | 플러그인 연결 가능, 미설치. 사용하려면 설치·계정 연결 필요 |
| **Canva** | 디자인 생성·편집·브랜드 키트 접근·여러 형식 내보내기 | SNS·명함·프레젠테이션 등 브랜드 응용물 | 현재 마켓에서 관리자 비활성화 상태. 즉시 연결 가능한 후보 아님 |

### Recraft: 벡터 보완에 가장 직접적인 후보

현재 공식 안내는 `https://mcp.recraft.ai/mcp`의 호스팅 원격 서버입니다. OAuth 2.0과 Streamable HTTP를 사용하며 브라우저 로그인으로 인증합니다. Recraft Studio와 구독 크레딧을 공유하고, 제한된 무료 할당과 유료 월간·추가 크레딧 모델을 제공합니다. 과거 로컬 서버처럼 별도 API 키를 전달할 필요가 없습니다. [현재 공식 MCP 문서](https://www.recraft.ai/docs/mcp-reference/remote-server)

기존 `recraft-ai/mcp-recraft-server` 저장소는 2026-07-13 보관 처리되었고 README에 deprecated 및 원격 서버 이동 안내가 있습니다. 옛 npm 로컬 서버 설치 절차는 추천하지 않습니다. [이전 공식 저장소와 이전 안내](https://github.com/recraft-ai/mcp-recraft-server)

로컬 Codex CLI의 `mcp add --help`, `mcp login --help`에서 URL 등록·로그인 명령을 확인했습니다. 다음은 미실행 연결 예시이며, 실제 연결·도구 호출·SVG 결과 품질은 확인하지 않았습니다.

```bash
codex mcp add recraft --url https://mcp.recraft.ai/mcp
codex mcp login recraft
```

### Figma: 가이드·시스템 편집용

공식 write-to-canvas 문서는 Codex를 지원 클라이언트로 명시하고, 편집을 위해 Full seat와 파일 편집 권한을 요구합니다. 네이티브 레이아웃과 컴포넌트·변수 생성이 가능하지만 이미지 assets와 커스텀 폰트에는 제한이 있습니다. 따라서 생성된 로고 PNG가 자동으로 완성된 Figma 브랜드 키트가 된다고 약속할 수는 없습니다. 브랜드 가이드 구조·컬러 토큰·레이아웃 협업에 더 적합합니다. [공식 문서](https://developers.figma.com/docs/figma-mcp-server/write-to-canvas/)

### Canva: 브랜드 응용물 확장용

공식 MCP는 디자인 생성·편집·브랜드 키트 접근·내보내기를 제공합니다. 현재 도구 문서상 브랜드 키트·autofill·템플릿 관련 도구는 Pro 이상 플랜을 요구합니다. 일부 플러그인 소개에 남은 Enterprise 한정 설명보다 현재 공식 도구 문서를 우선했습니다. 이 세션에서는 Canva와 Adobe/Adobe Express가 관리자에 의해 비활성화되어 있어 바로 설치·연결할 수 있는 상태가 아닙니다. [MCP 안내](https://www.canva.dev/docs/apps/mcp/), [도구별 플랜 조건](https://www.canva.dev/docs/apps/mcp/tools/)

## 제안하는 적용 순서

1. **브랜드 전략**: `brand-context`·`brand-identity`의 출력 형식을 참고해 기존 Logopia 브리프에 의미·차별성·응용 환경을 보강합니다. 기존 사용자 입력을 다시 받지 않도록 연결합니다.
2. **브랜드 보드**: `brandkit`의 구성법을 참고해 선택된 로고의 디지털·실물 응용 시안을 만듭니다. 한 장의 보드 이미지와 납품용 개별 자산을 구분합니다.
3. **벡터**: 실제 SVG가 필요할 때 Recraft 원격 MCP를 검토합니다. 선택된 PNG와 벡터 결과의 형태·글자·작은 크기·단색 재현을 비교하는 별도 검증이 필요합니다.
4. **편집·협업**: Figma에 가이드와 토큰을 구성하고, Canva 접근이 가능해지면 SNS·인쇄물 등의 응용 템플릿을 확장합니다.

이 순서는 본 조사에 따른 제안입니다. 구현이나 계정 연결은 이번 요청 범위에서 수행하지 않았습니다.

## 조사 방법과 지표 해석

- [skills.sh 리더보드](https://www.skills.sh/)를 먼저 확인한 뒤 `npx --yes skills find logo`, `branding`, `'brand identity'`, `logo-creator`를 검색했습니다. 검색 결과에 무관한 스킬이 섞여 있어 저장소의 실제 `SKILL.md`와 필요한 스크립트를 읽어 구분했습니다.
- 라이선스와 기능은 가능하면 위 링크의 고정 커밋에서 확인했고, stars는 2026-10-01 GitHub REST API 응답을 사용했습니다. 별 수는 스킬 한 개가 아닌 전체 저장소 지표입니다.
- 설치 수는 skills.sh 또는 검색 CLI의 표시값이며 갱신 시점·표시 범위에 따른 차이가 관찰되었습니다. 품질이나 유지보수 수준의 직접 증거로 취급하지 않았습니다.
- Codex 대상 설치 문법은 Skills CLI가 공개한 `--agent codex`, `--skill` 옵션을 확인했습니다. 표준 스킬 형식의 적용 가능성과 실제 외부 서비스의 연결·실행 성공은 별개입니다. [Skills CLI 공식 README](https://github.com/vercel-labs/skills#available-options)
