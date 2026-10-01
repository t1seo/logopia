# 변경 전 워크플로 자료

기준 소스는 Git `4d102c260ec1b65e086ab5f5699cee4ffcbdad01`, helper 패키지 `0.8.0`입니다. 해당 커밋의 `skills/logo-land`, `pyproject.toml`, `uv.lock`을 별도 임시 디렉터리에 `git archive`로 복원해 실행했습니다. 따라서 작업 중 생산 파일이 바뀌어도 이 baseline에는 반영되지 않습니다. 실행 환경은 `uv run --locked --project <복원 소스> python ...`이며 CPython 3.13.11이 선택되었습니다.

## 사전에 고정한 조건

[공통 원문 브리프](../briefs/)와 [실험 프로토콜](../protocol.json)을 프롬프트 생성 전에 기록했습니다. 세 브리프 모두 한 방향·한 후보를 요청합니다. 변경 전 3회와 개선 후 3회, 총 6회 생성·0회 수정·0회 재시도가 계획되어 있습니다. 각 원본과 최종 입력을 그대로 보존하며, 주관적으로 마음에 들지 않는 후보도 재생성하거나 비교에서 빼지 않습니다.

TIDE는 문자 없는 추상 심볼, 모아는 정확한 한글 `모아`만 쓰는 워드마크, Folio는 작은 심볼과 정확한 영문 `Folio`를 함께 배치한 가로형 로고입니다. TIDE와 모아는 사용자가 순백색 배경을 명시한 조건이며, Folio는 불투명 배경색 선택을 위임한 조건입니다. 배경 조건은 개선판에서도 같습니다.

Baseline은 기존 스킬을 일부러 약하게 작성한 프롬프트가 아닙니다. 현재 `SKILL.md`와 `logo-craft.md`를 따라 제품 의미, 구체적인 형태·간격, 색상 역할, 사용 크기와 관찰할 위험을 concept에 담았습니다. 모아에는 `lettering.md`, Folio에는 `typography.md`를 적용했습니다. 기본 로고 타입과 palette/lockup의 실제 helper 출력도 그대로 보존했습니다.

색상은 기존 `color-workflow.md`의 제안을 역할에 맞게 사용했습니다. TIDE는 Quiet technology의 blue/cyan, 모아는 Editorial craft의 muted red를 선택했습니다. 필요 없는 색을 억지로 추가하지 않았고, 명시적 흰 배경 조건은 지켰습니다. Folio는 같은 문서의 Editorial craft 세 색을 symbol/name/paper surface에 적용했습니다. Folio의 `#EDE4D5` 선택은 기존 가이드에 근거한 의도이므로, 실제 결과가 beige라고 해서 사용자 지시 불이행으로 판정하지 않습니다. 브랜드 적합성과 새 기본값의 차이를 비교할 사례입니다.

모든 구조화 팔레트는 advisory입니다. exact foreground HEX, 최대 색 수 등의 사용자 제한을 새로 발명하지 않았습니다. 배경·색상 역할·가독성은 시각적으로 평가하며, PNG의 모든 픽셀을 exact HEX와 일치시키는 export gate는 이 비교에 사용하지 않습니다.

## 생성에 사용할 실제 입력

| 사례 | 공통 원문 | Helper JSON | 최종 prompt TXT |
|---|---|---|---|
| TIDE | [brief](../briefs/tide.json) | [prompt](prompts/tide.json) | [정확한 입력](prompts/tide.txt) |
| 모아 | [brief](../briefs/moa.json) | [prompt](prompts/moa.json) | [정확한 입력](prompts/moa.txt) |
| Folio | [brief](../briefs/folio.json) | [prompt](prompts/folio.json) | [정확한 입력](prompts/folio.txt) |

각 TXT는 대응 JSON의 `prompt` 문자열을 `jq -r .prompt`로 추출한 것입니다. 공백을 포함한 별도 스타일 문구를 덧붙이지 않습니다. 실제 이미지 도구의 `prompt` 인자로 사용하고, 새 이미지이므로 `referenced_image_paths`와 `num_last_images_to_include`는 모두 생략합니다. Native 도구에 seed/model 설정이 노출되지 않아 동일 픽셀 재현은 보장하지 않습니다.

## Helper 실행과 import

이번 로컬 경로는 [local-workspace.txt](local-workspace.txt)에 기록했습니다. 그 아래 `source`가 고정 소스이고, `workspace`는 session 저장소입니다. 임시 디렉터리는 새 clone의 배포 자료가 아닙니다.

아래는 실제 실행한 명령의 형태입니다. 세 사례에 `tide`, `moa`, `folio`를 각각 적용했습니다. `--concept`는 [inputs/](inputs/)의 해당 파일 전체를 안전하게 인자로 전달했습니다. Folio의 lockup은 처음 brief에 저장했습니다.

```sh
quality_root="$PWD/docs/qa/brand-output-quality-2026-10-01"
quality_tmp=$(cat "$quality_root/baseline/local-workspace.txt")
quality_id=tide
quality_helper="$quality_tmp/source/skills/logo-land/scripts/logo_project.py"

uv run --locked --project "$quality_tmp/source" python "$quality_helper" \
  --workspace "$quality_tmp/workspace" init \
  --session "baseline-$quality_id" \
  --brief "$quality_root/baseline/inputs/$quality_id-brief.json"

uv run --locked --project "$quality_tmp/source" python "$quality_helper" \
  --workspace "$quality_tmp/workspace" palette-add \
  --session "baseline-$quality_id" --palette advisory-v1 \
  --palette-file "$quality_root/baseline/inputs/$quality_id-palette.json" --revision 0

quality_concept=$(cat "$quality_root/baseline/inputs/$quality_id-concept.txt")
uv run --locked --project "$quality_tmp/source" python "$quality_helper" \
  --workspace "$quality_tmp/workspace" prompt \
  --session "baseline-$quality_id" --concept "$quality_concept" --palette advisory-v1
```

기존 session에서 `init` 또는 `palette-add`를 반복하지 말고, 별도 workspace에 같은 입력을 사용해 주세요. 고정 builder와 입력을 사용한 뒤 생성한 prompt를 저장본과 비교해 주세요. 이번 prompt 생성 시점의 revision은 모두 1이고, palette ID는 `advisory-v1`입니다.

실제 native 이미지가 반환된 후 import하는 예시입니다. `quality_image`에는 해당 호출에서 반환된 PNG의 정확한 경로를 지정합니다. 가장 최근 파일을 자동 선택하지 않습니다. 시각 검토 이전에 선택·승인·export를 실행하지 않습니다.

```sh
quality_image='/actual/native/output/tide.png'
uv run --locked --project "$quality_tmp/source" python "$quality_helper" \
  --workspace "$quality_tmp/workspace" import \
  --session "baseline-$quality_id" --artifact a-v1 \
  --image "$quality_image" \
  --prompt-file "$quality_root/baseline/prompts/$quality_id.txt" \
  --palette advisory-v1 --background opaque --revision 1
```

[receipts/](receipts/)는 실제 init/palette-add 응답입니다. [source/](source/)에는 사용한 스킬·핵심 builder·가이드 원문과 SHA-256을 보존했습니다. [입력 해시](input-sha256.txt)로 브리프와 프롬프트가 생성 이후 바뀌지 않았는지 확인할 수 있습니다. 이 준비 단계만으로 이미지를 생성했거나 아웃풋이 좋아졌다고 주장하지 않습니다.

## 실제 원본 import와 기술 측정

부모 에이전트가 native 도구로 생성한 세 PNG를 위 명령으로 import했습니다. [observed-technical.json](observed-technical.json)에 실제 크기·alpha·원본/복사본/import 파일 SHA-256·prompt SHA-256을 기록했습니다. 각 import에서 반환된 full-image report와 추가 `color-analyze`의 실제 응답은 [measurements/](measurements/)에 보존했습니다. 네 모서리의 빈 16×16 영역을 각각 분석했으며, 현재 로컬 session revision은 모두 6입니다. 선택·시각 승인·export는 실행하지 않았습니다.

TIDE는 1254×1254, 모아는 1774×887, Folio는 1665×945 PNG이며 모두 alpha 255인 불투명 파일입니다. 생성 원본, 이 문서의 복사본, helper import 복사본의 해시가 각각 일치합니다. 출력 비율과 실제 로고 주변 여백이 다르므로 CSS에서 동일 폭을 지정해도 로고 자체의 크기가 동일하다는 뜻은 아닙니다. 원본을 자르거나 늘여 맞추지 않습니다.

세 full-image report는 모두 advisory `pass`를 반환했습니다. 이는 정확한 글자, 형태의 완성도, 색의 역할 배치나 브랜드 적합성이 승인됐다는 뜻이 아닙니다. TIDE와 모아의 네 코너 대표 quantized swatch는 모두 `#FEFEFE`이며, Folio는 코너에 따라 `#EBE2D2`, `#EDE4D4`, `#EBE2D2`, `#ECE3D3`입니다. 대표색과 허용오차 기반 target match는 해당 표본의 측정값이며 전체 배경의 모든 픽셀이 순백색 또는 의도 HEX와 같음을 증명하지 않습니다.
