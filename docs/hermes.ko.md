# Hermes로 로고 만들기

[English](hermes.md) · [한국어](hermes.ko.md) · [Logopia](../README.ko.md)

브랜드를 한 번 설명해 주세요. Hermes가 서로 다른 디자인 방향을 만들고, 원본을 생성한 뒤, 두 번의 별도 이미지 검토를 거쳐 선택하신 후보를 다듬습니다.

**브리프 → 방향 제안 → 원본 후보 → 이미지 검토 → 선택 → 부분 수정 → 전달**

## 대화 시작하기

macOS 또는 Linux의 [Hermes Agent](https://hermes-agent.nousresearch.com/), Hermes에서 작동하는 이미지 생성 제공자, Python 3.12 이상과 `uv`가 필요합니다. 이 네이티브 플러그인은 Hermes의 공개 플러그인·이미지 입력 API를 사용하며 Hermes의 Python 3.11 이상 환경을 지원합니다. 로컬 파일 보조 도구는 저장소에 고정한 Python 3.12 이상 환경에서 별도로 실행합니다. 설치 명령은 플러그인과 의존성(Pydantic 2.12 이상 3 미만, Pillow 11.2 이상 13 미만)을 검사하며, Hermes 설치나 이미지 제공자 설정을 대신하지 않습니다.

Logopia 저장소에서 전용 프로필을 한 번 만들고 모델과 도구를 설정해 주세요.

```sh
uv sync --locked
hermes profile create logopia --no-alias --no-skills
hermes -p logopia setup
uv run --locked python integrations/hermes/studio.py install --profile logopia
hermes -p logopia chat --toolsets logopia-studio,image_gen --skills logopia-studio:director
```

프로필이 이미 있다면 생성 단계를 건너뛰고 기존 설정을 사용해 주세요. 설치 시 전체 과정을 마칠 수 있도록 해당 이름 있는 프로필의 네이티브 순차·동시 도구 실행 제한(`timeouts.tools.sequential_call`, `timeouts.tools.concurrent_batch`)을 각각 1,800초, 즉 30분으로 설정합니다. 프로필의 기존 제공자·모델 선택과 기본 프로필은 유지됩니다. 다른 프로젝트에서 사용하려면 설치 명령에 `--workspace /absolute/path/to/project`를 추가해 주세요.

업데이트가 중단되면 가능한 경우 이전 플러그인을 복원합니다. 다른 파일이 그 자리를 차지했거나 복원에 실패하면 이전 파일은 해당 프로필의 `plugins/.logopia-install-*/previous`에 보존됩니다. 설치가 복구될 때까지 이 복구용 사본을 유지해 주세요. 중단된 업데이트를 성공으로 표시하지 않습니다.

이렇게 요청하실 수 있습니다.

> 재사용 목재로 수리 가능한 가구를 만드는 OFFCUT의 로고 후보를 세 개 만들어 주세요. 고객은 작은 도심 주택에 사는 사람들입니다. 따뜻하고 기지가 있으면서 정교한 느낌을 원합니다. 기억하기 쉬운 심볼과 정확한 글자 OFFCUT을 흰색 배경에 조합하고, 전체 로고를 192px 너비에서도 비교해 주세요.

비교 화면에서 원본 PNG를 바로 열 수 있습니다. 디자인 방향, 작은 크기 미리보기, 구체적인 검토 내용과 이전 버전도 함께 표시합니다. 화면을 둘러보거나 피드백 초안을 작성하는 것만으로 저장된 선택이 바뀌지는 않습니다.

## 선택하고 다듬기

화면에서 후보를 고르고 **유지할 점**과 **바꿀 점**을 작성한 뒤, 복사한 요청을 Hermes에 보내 주세요.

> 심볼과 OFFCUT 글자, 색은 유지해 주세요. 심볼과 글자 사이를 조금 더 벌리고, 심볼 안쪽의 좁은 틈을 넓혀 주세요.

수정은 선택한 정확한 원본을 기준으로 진행하며, 수정본은 새로 검토합니다. 이전 원본도 남습니다. 필요한 검사를 통과한 후보의 전달을 요청해 주세요. 후보를 선택하는 것만으로 품질 검토를 통과한 것으로 처리하지 않습니다.

## 실제 사례: OFFCUT

[OFFCUT 사례](hermes-demo/README.ko.md)는 최초 후보 3개와 네이티브 수정 2개를 **c1 → e1 → e2**의 정확한 계보로 보존합니다. 첫 수정본은 글자 간격을 개선했지만 심볼과 글자 사이의 틈이 줄어 보존 검사를 통과하지 못했습니다. 최종 e2는 그 틈을 복원하고 두 모델 검토를 통과했으며 작업 버전 47에서 전달됐습니다. [최초 c1 PNG](hermes-demo/originals/c1.png)와 [다듬은 e2 PNG](hermes-demo/originals/e2.png)를 비교하거나 실제 [전달 ZIP](hermes-demo/delivery/logo-package.zip)을 내려받으실 수 있습니다.

이 공개 사례는 코디네이터의 선택을 기록한 자료이며, 사용자의 승인이나 재개 가능한 비공개 작업 상태는 아닙니다. 폴더를 내려받아 `index.html`을 로컬에서 열면 오프라인으로 비교하실 수 있습니다. [실행 기록](qa/hermes-workflow/native-run.md)에는 최초 네이티브 도구 제한 420초로 인한 중단과, 이미지 작업을 추가하지 않은 명시적 검토 전용 복구도 남아 있습니다.

## 저장한 작업 이어가기

Hermes에 작업 상태를 물어보거나 아래 명령에서 `offcut-hermes-demo`를 저장된 작업 ID로 바꿔 사용해 주세요. 상태 조회와 비교 화면 생성에는 이미지 모델을 호출하지 않습니다.

```sh
uv run --locked python integrations/hermes/studio.py show --workflow offcut-hermes-demo
uv run --locked python integrations/hermes/studio.py gallery --workflow offcut-hermes-demo
```

JSON으로 저장한 도구 요청은 실행 시간이 제한된 런처를 사용합니다. Hermes를 시작하기 전에 정확한 작업 버전을 검사하며, 후보를 대상으로 하는 작업은 원본 해시도 확인합니다.

```sh
uv run --locked python integrations/hermes/studio.py run --profile logopia --request request.json
```

런처 자체의 제한 시간은 기본 30분이며, `--timeout`으로 1~3,600초를 지정할 수 있습니다. 종료 시 정상 종료 유예 10초 뒤 강제 종료 확인에 최대 10초를 더 사용하며, 실행 중인 PID 조회도 정해진 시간 안에 정리합니다. 로컬 보조 도구를 포함해 자신이 만든 세션의 프로세스 그룹을 확인합니다. 이름 있는 프로필의 네이티브 도구 제한과는 별개의 설정입니다. 프로세스 종료 코드나 Hermes의 마지막 설명만으로 성공을 판단하지 않고 저장된 작업 결과를 확인합니다. 로컬 프로세스가 종료되어도 이미지 제공자의 요청이 취소됐다고 단정하지 않습니다.

오래된 피드백이 거부되면 최신 상태를 확인하고 변경을 다시 적용해 주세요. 중단된 이미지 요청의 결과가 불명확하면 자동으로 재생성하지 않습니다. 완료된 원본은 `.logo-generator/sessions/`, 작업 결정은 `.logo-generator/workflows/`에 남습니다.

이미지를 읽는 검토만 실패하거나 중단됐다면 저장한 작업을 이어 달라고 명시적으로 요청해 주세요. 복구 조건을 충족한 후보는 남은 검토 기회를 한 번 사용하며 이미지를 새로 만들지 않고 실패 이력도 유지합니다. 결과가 불명확한 이미지 요청은 기록된 정확한 결과를 확인할 때까지 차단하며, 자동 재시도·캐시 파일 추측·새 원본 생성은 하지 않습니다. 처음의 생성 요청을 반복해도 실패하거나 중단된 작업을 다시 시작하지 않습니다.

## 지원 범위

- 브랜드 로고, 제품에 맞춘 앱 아이콘과 IP 캐릭터를 만듭니다. 앱 방향에는 고유한 Mark, 짧은 Lettering, 오브젝트, 유기적 형태, 캐릭터, 모듈형 기하학 등을 선택할 수 있습니다. IP의 주제·비례·표정·색은 브리프를 따르며 귀여움이나 고정 팔레트를 기본값으로 강제하지 않습니다.
- 빠른 생성은 기존대로 브랜드·앱 3개, IP 6개입니다. 기존 `count`는 1~6개를 지원합니다. `direction_count: 3`과 `candidates_per_direction: 3`을 명시하면 서로 다른 3개 방향에서 조형을 달리한 후보를 각각 3개씩 만듭니다. 탐색 필드와 `count`를 함께 지정하지 마세요. 최초 생성은 최대 9개, 요청한 수정은 최대 2회이며 실패하거나 결과가 불명확한 이미지 호출도 예약 예산을 사용합니다.
- 브랜드와 앱에 한글을 포함한 정확한 글자를 요청할 수 있으며, 이름을 임의 이니셜로 바꾸지 않습니다. 생성된 철자는 직접 확인해 주세요. 앱·IP 경로는 배경을 채운 정사각형이며 IP 초상에는 글자를 넣지 않습니다. 선택적인 `app_icon` 메타데이터에 글자를 넣을 때는 Helper의 Monogram 계약인 공백·제어문자 없는 Unicode 코드 포인트 1~8개를 따릅니다. 브랜드의 투명 PNG도 계속 지원합니다.
- 해시를 검증한 로컬 PNG Reference 최대 6개를 두 계획 호출과 이미지 검토에 실제로 전달합니다. 관찰·해석·참고할 특성은 구분하여 저장합니다. 생성에는 선택한 특성을 **텍스트 Conditioning**으로 전달합니다. Hermes의 `image_generate`는 `image_url` 하나를 지원하며 정확한 수정 부모용으로 보존하므로 `reference_conditioning: image` 요청은 명시적으로 거부합니다. Negative Reference는 피할 특성에 사용하며 자동 Reference를 사용자 취향으로 저장하지 않습니다. Reference 필드는 [입력 계약](../integrations/hermes/CONTRACT.md)을 참고해 주세요.
- 색상 제안과 후보당 모델 검토 호출 두 번을 저장된 검토 예산 안에서 지원합니다. 요청한 수정은 글자·색·배경을 유지하며 디자인·레터링과 제작·사용 크기를 다시 검토합니다. 이 조건을 바꾸려면 새 브리프를 사용하며, 엄격한 팔레트는 기존 [`$logo-land` Codex 스킬](../skills/logo-land/SKILL.md)을 이용해 주세요. AI 관찰, 사용자 선택, 플랫폼 검증은 별개입니다.
- 앱 Gallery에서 원본을 변경하지 않고 32/48/64/128px, 밝고 어두운 주변 배경, 동일한 48px 사용 맥락과 CSS Mask 시뮬레이션을 비교합니다. 이 진단 크기와 시뮬레이션은 실제 OS 렌더링이나 플랫폼 통과 증거가 아닙니다. 별도의 [블라인드 선호 비교](preference-review.md)는 Helper에서 제공합니다.
- 결과는 원본 래스터 PNG와 검사를 통과한 전달 패키지입니다. Hermes 네이티브 경로는 평면 Concept artwork를 만들며 선택적인 플랫폼·Appearance 메타데이터가 편집 가능한 Layer를 만들지는 않습니다. Apple Layered, Android Adaptive, 크기를 검증한 Store Asset은 [Helper Asset Handoff](icon-assets.md)를 이용해 주세요. 편집 가능한 벡터, 폰트 파일과 상표 확인은 별도 작업입니다.

예를 들어 아래 네이티브 `logopia_start` 입력을 `request.json`으로 저장하고 위의 `studio.py run` 명령으로 실행하실 수 있습니다.

```json
{
  "workflow_id": "reading-exploration",
  "brief": {
    "name": "틈",
    "exact_text": "틈",
    "product": "짧은 독서 시간을 기록하는 앱",
    "audience": "출퇴근 중 읽는 독자",
    "personality": "조용하고 또렷함",
    "use_case": "앱 아이콘",
    "mode": "app_icon",
    "logo_type": "lettermark",
    "display_width": 48,
    "direction_count": 3,
    "candidates_per_direction": 3
  }
}
```

빠른 생성은 탐색 필드 두 개를 생략하시면 기존대로 3개를 만듭니다. 기존에 저장한 프롬프트·원본·선택은 보존되며 새 선택 필드 때문에 자동 재생성하지 않습니다.

IP 방향은 [s1dashu/ip-as-logo-skill](https://github.com/s1dashu/ip-as-logo-skill)을 참고하여 각색했으며, [MIT 고지](../integrations/hermes/skills/director/references/ip-as-logo.LICENSE)를 포함합니다.
