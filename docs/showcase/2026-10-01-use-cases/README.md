# October experiments — user rejected design quality

[Logopia](../../../README.md#use-cases) · [한국어 소개](../../../README.ko.md#use-cases) · [Visual gallery](../../gallery.md#showcase) · [Open offline HTML](index.html) · [Generation manifest](manifest.json)

**Status: the user rejected the design quality of all six October 1, 2026 results, including the displayed corrected versions.** They found no meaningful improvement and no production-ready result. Output-quality improvement remains unproven. Browser QA passed usability checks only; it did not establish design quality or acceptance.

**사용자는 수정된 표시본을 포함한 여섯 결과 모두 의미 있는 개선이 없고 실사용 수준에 미치지 못한다고 판단하여 디자인 품질을 거절했습니다.** 품질 개선은 입증되지 않았습니다. 브라우저 QA는 사용성만 통과했으며 디자인 품질이나 수용을 뜻하지 않습니다.

Six fictional brands, six different requests: Latin and Hangul wordmarks, an integrated monogram, an abstract symbol, a symbol with a name, and a character app icon. Each image links to its original PNG; each saved prompt is the complete native generation or edit request for the displayed result. The shorter requests below explain how to start a similar conversation.

2026년 10월 1일에 생성한 가상 브랜드 예제 여섯 개입니다. 이미지를 누르면 원본 PNG를, 프롬프트 링크를 누르면 실제 생성 요청을 보실 수 있습니다. 아래의 짧은 요청 예시는 대화를 시작하기 위한 설명입니다.

<table>
  <tr>
    <td align="center" width="50%"><a href="./images/01-mori.png"><img src="./images/01-mori.png" width="400" alt="mori in rounded forest-green lowercase letters with a lime dot"></a><br><strong>mori</strong><br><sub>Latin wordmark · Plant subscription</sub></td>
    <td align="center" width="50%"><a href="./images/02-sai.png"><img src="./images/02-sai.png" width="400" alt="사이 in rounded cobalt and coral Hangul on white"></a><br><strong>사이</strong><br><sub>Hangul wordmark · Reading club</sub></td>
  </tr>
  <tr>
    <td align="center" width="50%"><a href="./images/03-al.png"><img src="./images/03-al.png" width="400" alt="Indigo serif A and L sharing one structure on lilac"></a><br><strong>AL</strong><br><sub>Integrated monogram · Architecture studio</sub></td>
    <td align="center" width="50%"><a href="./images/04-tandem.png"><img src="./images/04-tandem.png" width="400" alt="Two teal and cobalt curved forms around open white space, without text"></a><br><strong>Tandem</strong><br><sub>Abstract symbol · Shared planning</sub></td>
  </tr>
  <tr>
    <td align="center" width="50%"><a href="./images/05-pebble.png"><img src="./images/05-pebble.png" width="400" alt="Terracotta pebble with a white path beside the lowercase plum word pebble"></a><br><strong>pebble</strong><br><sub>Symbol + wordmark · Walking journal</sub></td>
    <td align="center" width="50%"><a href="./images/06-pip.png"><img src="./images/06-pip.png" width="400" alt="Orange bird with a plum eye and beak in the lower-right of a lilac square"></a><br><strong>Pip</strong><br><sub>Character app icon · Daily voice notes</sub></td>
  </tr>
</table>

These experiments were made with the **unreleased 0.10.0 source**. Original images, requests and observations remain available as records of rejected work. They do not establish output-quality improvement. The brands imply no real-world affiliation or trademark clearance. Outputs are raster PNGs; editable vectors, font files and platform-specific app icon packages are separate work.

현재 **미발행 0.10.0 소스**로 진행한 실험입니다. 거절된 작업의 원본·요청·관찰을 보존했으며, 결과물의 품질 개선은 입증하지 못했습니다. 브랜드 제휴나 상표 사용 가능성을 뜻하지 않으며, 편집 가능한 벡터·서체·플랫폼별 아이콘 패키지는 별도 작업입니다.

<a id="01-mori"></a>

## mori · Latin wordmark

**Use case:** Plant subscription. **Palette intent:** Forest green + lime.

> $logo-land Create a wordmark using the exact lowercase text mori for a plant subscription. Use forest green and lime; make the letters the design, with no separate icon.

> $logo-land 식물 구독 서비스 mori의 워드마크를 만들어 주세요. 정확한 글자는 mori이며, 포레스트 그린과 라임을 사용하고 별도 아이콘 없이 글자 자체를 디자인해 주세요.

**Observed result:** The exact lowercase mori is readable, with broad rounded green letters, an open o counter and a lime dot.

**Limit:** The soft rounded style is relatively generic. The image supplies no editable font or verified typeface provenance.

**관찰:** 정확한 소문자 mori가 읽히며, 굵고 둥근 초록색 글자와 열린 o 내부 공간, 라임색 점을 확인했습니다.

**한계:** 부드럽고 둥근 스타일은 비교적 일반적입니다. 편집 가능한 서체나 검증된 폰트 출처는 제공하지 않습니다.

[Original PNG](images/01-mori.png) · [Exact saved native request](prompts/01-mori.txt)

<a id="02-sai"></a>

## 사이 · Hangul wordmark

**Use case:** Reading club. **Palette intent:** Cobalt + coral.

> $logo-land Create a Hangul wordmark for a reading club using only the exact text 사이. Use cobalt and coral, with clear, friendly letterforms.

> $logo-land 독서 모임의 한글 워드마크를 만들어 주세요. 정확한 글자 사이만 사용하고, 코발트와 코랄로 친근하면서 또렷하게 읽히는 글자를 표현해 주세요.

**Observed result:** The exact Hangul 사이 is readable: rounded cobalt 사 and coral 이 on white. A native edit corrected the first result’s unexpected transparency and stray edge fragments.

**Limit:** The broad rounded lettering does not establish a distinctive type system or an editable font. Minimum readable size is not established.

**관찰:** 정확한 한글 사이가 읽히며, 둥근 코발트 사와 코랄 이가 흰 배경에 놓여 있습니다. 첫 결과의 의도하지 않은 투명 배경과 외곽 조각은 네이티브 편집으로 수정했습니다.

**한계:** 굵고 둥근 글자만으로 고유한 타이포그래피 체계나 편집 가능한 서체를 제공하는 것은 아닙니다. 최소 가독 크기는 입증하지 않았습니다.

[Original PNG](images/02-sai.png) · [Exact saved native edit request](prompts/02-sai.txt)

<a id="03-al"></a>

## AL · Integrated monogram

**Use case:** Architecture studio. **Palette intent:** Indigo.

> $logo-land Create one integrated AL monogram for an architecture studio in indigo. Keep both exact initials recognizable within a shared structure.

> $logo-land 건축 스튜디오의 이니셜 AL을 하나로 결합한 모노그램을 인디고로 만들어 주세요. 구조를 공유하되 두 글자를 알아볼 수 있게 해 주세요.

**Observed result:** A readable indigo A and L share a compact structure on lilac, with visible serif details.

**Limit:** The A uses a thinner stroke than the L, leaving uneven stroke balance. Small-size legibility is not established.

**관찰:** 라일락 배경 위 인디고 A와 L이 간결한 구조를 공유하며, 세리프 디테일이 보입니다.

**한계:** A의 획이 L보다 얇아 획의 무게가 고르지 않습니다. 작은 크기의 가독성은 입증하지 않았습니다.

[Original PNG](images/03-al.png) · [Exact saved native request](prompts/03-al.txt)

<a id="04-tandem"></a>

## Tandem · Abstract symbol

**Use case:** Shared planning. **Palette intent:** Teal + cobalt.

> $logo-land Create a symbol for a shared planning service using teal and cobalt. Express coordination through one compact mark, with no lettering.

> $logo-land 공동 일정 계획 서비스의 심볼을 틸과 코발트로 만들어 주세요. 하나의 간결한 마크로 협업을 표현하고 글자는 넣지 말아 주세요.

**Observed result:** A larger teal curve and smaller cobalt curve frame an open central space, with no lettering. A native edit cleaned the first result’s edges and restored a white background.

**Limit:** The connection to shared planning is the brief’s intent; audience recognition of that meaning has not been tested. A one-color version is not included.

**관찰:** 큰 틸 곡선과 작은 코발트 곡선이 열린 중앙 공간을 둘러싸며 글자는 없습니다. 첫 결과의 외곽을 네이티브 편집으로 정리하고 흰 배경을 복원했습니다.

**한계:** 공동 일정 계획과의 연결은 브리프의 의도이며, 사용자가 그 의미를 알아보는지는 검증하지 않았습니다. 단색 버전은 포함하지 않았습니다.

[Original PNG](images/04-tandem.png) · [Exact saved native edit request](prompts/04-tandem.txt)

<a id="05-pebble"></a>

## pebble · Symbol + wordmark

**Use case:** Walking journal. **Palette intent:** Terracotta + deep plum.

> $logo-land Create a symbol and wordmark for a walking journal using the exact lowercase text pebble. Pair terracotta with deep plum and keep the lockup simple.

> $logo-land 걷기 브랜드의 심볼과 워드마크를 만들어 주세요. 정확한 소문자 pebble을 사용하고, 테라코타와 딥 플럼으로 간결한 조합을 구성해 주세요.

**Observed result:** The exact lowercase pebble sits beside a terracotta pebble shape with a curved white path. Deep plum lettering forms a wide horizontal lockup.

**Limit:** The path narrows toward its upper end. The full lockup needs testing at its intended header size; a compact icon version is not included.

**관찰:** 테라코타 조약돌 안의 흰 곡선 길 옆에 정확한 소문자 pebble이 놓여 있습니다. 딥 플럼 글자로 가로형 조합을 구성했습니다.

**한계:** 길의 위쪽 끝이 가늘어집니다. 실제 헤더 크기의 검토가 필요하며, 작은 아이콘용 버전은 포함하지 않았습니다.

[Original PNG](images/05-pebble.png) · [Exact saved native request](prompts/05-pebble.txt)

<a id="06-pip"></a>

## Pip · Character app icon

**Use case:** Daily voice notes. **Palette intent:** Orange + lilac.

> $logo-land Create one app icon for a voice-note companion with one friendly flat orange bird on a lilac background. Use a bold, simple silhouette and no text.

> $logo-land 음성 메모 앱을 위해 라일락 배경에 친근한 오렌지색 새 한 마리를 넣은 아이콘을 만들어 주세요. 굵고 단순한 평면 실루엣을 사용하고 글자는 넣지 말아 주세요.

**Observed result:** One orange bird fills the lower-right of a lilac square, with a dark plum eye and beak, an upturned tail and no lettering.

**Limit:** Subtle tonal variation remains despite the flat-color intent. The artwork is not a platform-specific app icon package.

**관찰:** 라일락 정사각형의 오른쪽 아래를 오렌지색 새 한 마리가 채웁니다. 딥 플럼 눈과 부리, 위로 올라간 꼬리가 있으며 글자는 없습니다.

**한계:** 평면 단색 의도에도 미세한 색 농도 차이가 남아 있습니다. 플랫폼별 앱 아이콘 제출 패키지는 아닙니다.

[Original PNG](images/06-pip.png) · [Exact saved native request](prompts/06-pip.txt)

## Production record

Eight native image-tool calls produced this collection: six initial generations and two parent-based edits. The first 사이 and Tandem outputs had unexpected transparency and stray edge fragments; native edits supplied the displayed versions on white. The helper prepared and saved the requests; the native image tool generated and edited the PNGs.

The [manifest](manifest.json) records call counts, source version, final dimensions and file hashes. The earlier background/edge failures remain available with their original requests and receipts. Those technical corrections did not make the displayed designs acceptable: the user rejected all six final designs on quality.

| Preserved attempt | Original PNG | Initial request | Receipt |
|---|---|---|---|
| 사이 v1 | [PNG](revisions/02-sai-v1.png) | [Request](revisions/02-sai-v1.txt) | [Receipt](revisions/02-sai-v1.json) |
| Tandem v1 | [PNG](revisions/04-tandem-v1.png) | [Request](revisions/04-tandem-v1.txt) | [Receipt](revisions/04-tandem-v1.json) |

네이티브 이미지 호출은 최초 생성 6회와 부모 원본 기준 수정 2회, 총 8회입니다. 사이·Tandem의 첫 결과에 있었던 투명 배경과 외곽 조각을 실제 네이티브 편집으로 수정했습니다. 위 표에는 사용하지 않은 첫 결과·당시 요청·호출 기록을 보존했고, 각 예제의 프롬프트 링크는 현재 표시한 결과를 만든 최종 요청으로 연결됩니다. 배경·외곽 수정과 별개로 최종 디자인 여섯 개 모두 품질을 거절당했습니다.

## How to inspect these files

The HTML page works locally with this collection's images and prompts in place. It uses no network requests, external fonts or libraries. Filters narrow the visible use cases; image links open the original, and each card offers a direct PNG download. GitHub renders this Markdown page and the README thumbnails, but does not run the HTML page inline.

Palette descriptions record the requested direction, not measured color compliance. Readability, small-size behavior and suitability for a real brand need review in their intended context. The user explicitly rejected all six designs; none was selected or approved for production. Earlier collections remain historical records rather than an endorsed quality benchmark.

[September 20 collection — historical](../2026-09-20-lifestyle/README.md) · [Earlier output archive](../../gallery.md#historical-outputs)
