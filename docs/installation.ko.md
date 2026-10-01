# 설치

[English](installation.md) · [한국어](installation.ko.md) · [문서](README.ko.md) · [Logopia](../README.ko.md)

저장소에서 바로 사용하거나, 로컬 마켓플레이스에 등록하여 다른 프로젝트에서도 `$logo-land`를 사용하실 수 있습니다.

## 요구 사항

Codex 내장 이미지 생성·편집 도구, Python 3.12 이상과 `uv`가 필요합니다. 플러그인 설치만으로 없는 이미지 도구가 활성화되지는 않습니다. 별도의 OpenAI API 키나 다른 로고 서비스 계정은 필요하지 않습니다.

## 저장소에서 바로 사용

```sh
git clone https://github.com/t1seo/logopia.git
cd logopia
uv sync --locked
codex
```

이 폴더에서 연 Codex 대화에서 스킬을 읽도록 요청해 주세요.

> skills/logo-land/SKILL.md를 읽고 지침에 따라 로고를 만들어 주세요. 명상 스튜디오 고요의 차분한 시안 두 개를 보여 주시고, 심볼과 정확한 한글 고요를 조합해 주세요.

이 방법은 저장소의 지침을 직접 사용합니다. 아래 플러그인 설치를 완료하면 다른 프로젝트의 대화에서도 `$logo-land`를 사용하실 수 있습니다.

## Codex 플러그인으로 설치

이 저장소는 플러그인 소스를 제공하며, 공개 마켓플레이스나 릴리스 ZIP 설치 경로는 제공하지 않습니다. 저장소를 직접 로컬 마켓플레이스에 등록해 주세요.

1. 위 명령으로 저장소를 복제하고 **절대 경로**를 확인해 주세요.
2. `/absolute/path/to/local-marketplace`처럼 별도의 마켓플레이스 폴더를 정하고, 그 안에 `.agents/plugins/marketplace.json`을 만들어 주세요. 아래 JSON의 `path`를 저장소의 실제 절대 경로로 바꾸시고, Windows에서는 JSON 경로에 `/`를 사용해 주세요. 이미 마켓플레이스가 있다면 이름과 다른 항목을 유지하면서 플러그인 항목을 추가하고, 3단계에서 기존 마켓플레이스 이름을 사용해 주세요.

```json
{
  "name": "logo-land-local",
  "plugins": [
    {
      "name": "logo-land",
      "source": {
        "source": "local",
        "path": "/absolute/path/to/logopia"
      },
      "policy": {
        "installation": "AVAILABLE",
        "authentication": "ON_INSTALL"
      },
      "category": "Productivity"
    }
  ]
}
```

3. `.agents`가 들어 있는 **마켓플레이스 루트 폴더**를 등록하고 플러그인을 설치해 주세요. 예시 경로는 실제 마켓플레이스 위치로 바꿔 주세요.

```sh
codex plugin marketplace add /absolute/path/to/local-marketplace
codex plugin add logo-land@logo-land-local
```

4. **새 Codex 대화**를 열고 `$logo-land`로 시작해 주세요. 환경에서 별도 활성화를 요구하면 플러그인을 활성화해 주세요.

> $logo-land 제 브랜드에 어울리는 로고를 만들어 주세요.

위 구문은 2026-09-13 KST에 Codex CLI **0.154.0**의 아래 조회 전용 명령으로 확인했습니다. 설치된 CLI 버전이 다르면 해당 도움말을 확인해 주세요. [설치 기록](qa/installation.md)에는 이전에 실행한 설치와 검증 범위가 있습니다.

```sh
codex --version
codex plugin marketplace add --help
codex plugin add --help
```

## 소스·릴리스·설치 버전

현재 저장소의 Codex·Hermes manifest, Python 프로젝트와 잠금 파일의 보조 패키지는 **아직 발행하지 않은 0.9.0**입니다. 최신 발행본은 [v0.8.0 릴리스](https://github.com/t1seo/logopia/releases/tag/v0.8.0)이며, 복제 후 `git checkout v0.8.0`으로 선택하실 수 있습니다. 저장소 이름은 `logopia`이며, 플러그인 이름과 호출은 기존의 `logo-land`, `$logo-land`를 사용합니다.

기존 설치 캐시는 갱신 전까지 이전 버전일 수 있습니다. `0.9.0+codex.<timestamp>` 같은 로컬 버전은 캐시 갱신을 표시하며 공개 릴리스 발행을 뜻하지 않습니다. 소스 갱신과 재설치 후에는 새 대화를 시작해 변경된 스킬을 불러와 주세요. GitHub 소스 압축 파일은 저장소 스냅샷이며 자동 설치 프로그램이 아닙니다. [릴리스 안내](releases.md)와 [변경 이력](../CHANGELOG.md)을 참고해 주세요.

## 프로젝트 파일

작업은 `.logo-generator/sessions/<id>/`에 저장되며, 기본 전달 경로는 `output/logo-generator/<id>/`입니다. 이전 `logo-generator` 이름을 사용하는 호환 경로입니다. 새 대화에서는 `$logo-land`를 사용하시고, 기존 프로젝트 폴더 이름은 바꾸실 필요가 없습니다.

다른 작업 폴더에서 보조 명령을 실행할 때는 `uv run --locked --project /absolute/path/to/logopia`에 플러그인 루트를, 보조 명령의 `--workspace`에 프로젝트 폴더를 지정해 주세요. [프로젝트 파일 안내](../skills/logo-land/references/project-files.md)에 전체 명령과 스키마 1 마이그레이션·복구 범위를 설명했습니다. 백업과 PNG 원본을 보존해 주세요. 이전 v0.3.1 설치본이 스키마 2 프로젝트를 읽는다고 보장하지는 않습니다.

[요청 예시](../README.ko.md#이렇게-요청해-보세요) · [샘플 보기](samples/README.ko.md)
