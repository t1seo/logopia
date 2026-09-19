# 아이콘 조형 근거와 Reference 확인 기록

확인일: **2026-09-19**. 이 기록은 디자인 판단의 출발점이며 시장 점유율, 설치 전환율, 상표 고유성의 증거가 아닙니다. 이미지 관찰과 해석은 [references.json](references.json)에 따로 저장했습니다. 6개 사례 중 4개는 앱 아이콘, 2개는 브랜드 체계입니다. 모두 공식 출처의 실제 이미지를 내려받고 `view_image`로 열었습니다.

이미지 원본은 Git에서 제외된 `.logopia/reference-cache/`에만 있습니다. 공개 문서는 URL·SHA-256·상대 경로를 보관합니다. 캐시가 없는 새 checkout은 이미지를 확인한 상태가 아니며, 다시 읽기 전에는 이미지 conditioning에 쓰지 않습니다. 출처 표기는 사용 허가가 아닙니다. 연구자가 선정한 사례는 사용자 선호로 저장하지 않으며, 이 조사에서 외부 이미지 Provider로 전송하지 않았습니다.

## 구현에 적용할 구분

- **형태와 재질:** 각 방향에서 중심 실루엣, 접점·곡률·간격 중 실제 결정을 먼저 정하고 재질은 별도로 선택합니다. Craft의 공유 곡률과 간격, Gentler Streak의 비대칭 윤곽, Timer의 한 오브젝트는 서로 다른 해법입니다. 모두를 유리나 기하학으로 통일할 근거는 없습니다.
- **이름과 소형 표현:** Linear는 Wordmark, Mark, 타일형 Icon의 사용 맥락을 나눕니다. 전체 이름을 작은 타일에 밀어 넣거나 사용자 이름을 임의로 이니셜로 바꾸지 않습니다. [Linear 브랜드 가이드](https://linear.app/brand)
- **관찰과 가설:** Things는 2025년 발표에서 기존 파란 상자를 유지한 변경과 네 Appearance를 설명합니다. 이미지에서 확인한 것은 파란 프레임·밝은 면·체크의 반복입니다. 인지도 향상은 이 조사로 입증되지 않았습니다. [Things OS 26 발표](https://culturedcode.com/things/blog/2025/09/things-for-os-26/)
- **선택적 표현:** Friends of Figma 배지는 같은 둥근 부품과 전경 형태를 유지하며 주변 색·패턴을 바꿉니다. LogoLounge의 첫 글자 표현과 일부 글자 기울기 사례는 탐색 변수로만 사용합니다. 유명한 F 모양, 별, 궤도, 무한대를 기본값으로 채택하지 않습니다. [Figma 발표](https://www.figma.com/blog/friends-of-figma-brand-refresh/), [LogoLounge 2026 보고서](https://www.logolounge.com/trend/2026-logo-trend-report)
- **제품과의 관계:** Not Boring의 제품 소개는 3D·동작·소리를 실제 사용 경험의 일부로 설명합니다. 이것은 모든 앱 아이콘에 3D가 효과적이라는 증거가 아닙니다. Timer의 아이콘은 별도로 App Store 그림을 확인했습니다. [Not Boring](https://notbor.ing/), [Timer 제품](https://notbor.ing/product/timer)

## 플랫폼 정책의 근거

| 대상 | 확인한 지침과 적용 범위 |
| --- | --- |
| Apple layered icon | 가져온 **배경**은 full-bleed·불투명입니다. **전경**의 투명도는 허용됩니다. 정사각 원본 레이어에 시스템이 외곽 Mask를 적용하며, 미리 구운 하이라이트·블러·레이어 간 그림자는 동적 효과와 중복되는지 검토합니다. 평면 PNG에서 편집 가능한 레이어를 추정하여 만들었다고 표시하지 않습니다. [R1 HIG](https://developer.apple.com/design/human-interface-guidelines/app-icons) |
| Apple Appearance | 홈 화면의 default/dark/clear/tinted와 Icon Composer의 **Default/Dark/Mono** 편집 모드를 분리합니다. Composer의 Mono 옵션으로 clear/tinted 및 light/dark를 미리 봅니다. HIG의 iOS/iPadOS/macOS 표는 default, dark, clear light/dark, tinted light/dark입니다. [R2 Composer](https://developer.apple.com/icon-composer/), [공식 제작 안내](https://developer.apple.com/documentation/xcode/creating-your-app-icon-using-icon-composer) |
| Apple 기존 asset catalog | 별도 문서는 Dark PNG에 투명 배경, Tinted에 grayscale을 안내합니다. 이 경로에 layered 배경의 불투명 규칙을 일괄 적용하면 안 됩니다. [공식 asset catalog 안내](https://developer.apple.com/documentation/xcode/configuring-your-app-icon) |
| Android Adaptive launcher | foreground/background 및 선택적 monochrome을 별도 자산으로 다룹니다. 레이어는 108×108 **dp**, 핵심 로고는 48–66dp 범위입니다. R3의 도판은 66×66 경계를 표시하고, 공식 Codelab은 중앙 원형 안전영역을 설명합니다. 진단 가이드는 **지름 66/108의 중앙 원**을 보수적으로 사용하며 정사각 모서리까지 안전하다고 판정하지 않습니다. dp를 원본 px로 오인하지 않습니다. [R3 Adaptive icons](https://developer.android.com/develop/ui/compose/system/icon_design_adaptive), [공식 Codelab](https://developer.android.com/codelabs/basic-android-kotlin-compose-training-change-app-icon) |
| Google Play listing | 512×512 **px**, 32-bit PNG, sRGB, 최대 1024KB, 정사각 원본입니다. 외곽 그림자와 둥근 Mask는 Play가 적용하지만 내부 오브젝트 명암은 허용합니다. 불투명 배경은 권고이며 투명 자산은 Play UI 배경색을 드러냅니다. 따라서 alpha 존재를 무조건 실패시키지 않습니다. [R4 Play 규격](https://developer.android.com/distribute/google-play/resources/icon-design-specifications) |

CSS Mask·grayscale·32/48/64/128px 축소와 가상 홈 화면은 **진단 시뮬레이션**입니다. 실제 OS 렌더링, 빌드 가능한 native package, 플랫폼 심사 통과와 구별해야 합니다. 같은 크기·주변 배경에서 후보를 비교하고 원본을 보존합니다.

## 출처별 확인 범위

| ID | 공식 자료 | 확인 결과 |
| --- | --- | --- |
| R1 | [Apple HIG App icons](https://developer.apple.com/design/human-interface-guidelines/app-icons) | HTML은 JavaScript 안내만 반환했습니다. [동일 공식 DocC JSON](https://developer.apple.com/tutorials/data/design/human-interface-guidelines/app-icons.json)으로 본문·표·2026-06-08 변경 이력을 직접 확인했습니다. |
| R2 | [Icon Composer](https://developer.apple.com/icon-composer/) | 현재 제품 페이지와 공식 제작 문서 확인. 편집 모드는 Default/Dark/Mono입니다. |
| R3 | [Android Adaptive icons](https://developer.android.com/develop/ui/compose/system/icon_design_adaptive) | 본문과 foreground/background 도판을 직접 확인했습니다. 66 경계의 의미는 Codelab으로 보완했습니다. |
| R4 | [Google Play icon specifications](https://developer.android.com/distribute/google-play/resources/icon-design-specifications) | 본문 확인. 페이지 업데이트 표기는 2026-06-15입니다. 2019년 도입 지침을 2026년 신규 유행이라고 부르지 않습니다. |
| R5 | [Things for OS 26](https://culturedcode.com/things/blog/2025/09/things-for-os-26/) | 2025-09-15 발표와 실제 dock 비교 이미지 확인. 네 Appearance 중 내려받은 그림은 컬러 기본 표시입니다. |
| R6 | [Craft OS26](https://www.craft.do/os26) | 현재 홈페이지로 리디렉션됩니다. [2025-09-15 공식 업데이트](https://www.craft.do/blog/craft-update-3-2-6)로 맥락을 확인했습니다. Reference 그림은 현재 App Store 이미지이며, 2025년 그림과 동일하다고 주장하지 않습니다. |
| R7 | [LogoLounge 2026](https://www.logolounge.com/trend/2026-logo-trend-report) | 공식 보고서 본문 확인. 개별 사례의 출시 여부·원본 사용권은 검증하지 않아 이미지 Reference set에는 넣지 않았습니다. |
| R8 | [Friends of Figma refresh](https://www.figma.com/blog/friends-of-figma-brand-refresh/) | 2026-05-19 발표와 배지 이미지를 확인했습니다. 브랜드 시스템 사례이며 앱 아이콘이 아닙니다. |
| R9 | [Linear brand](https://linear.app/brand) | Wordmark·Mark·Icon 안내와 공식 ZIP의 세 PNG를 확인했습니다. ZIP 내부 수정일을 디자인 발표일로 사용하지 않았습니다. 원본의 변경·결합·관계 암시에 제한이 명시되어 있습니다. |
| R10 | [Gentler Streak](https://gentlerstories.com/gentlerstreak) | 공식 제품 페이지와 연결된 App Store 아이콘 확인. 특정 아이콘 디자인 발표일·홈 화면 Appearance는 unknown입니다. |
| R11 | [Not Boring](https://notbor.ing/) | 공식 제품 소개와 연결된 Timer의 App Store 아이콘을 각각 확인했습니다. 제품 UI의 3D 표현을 아이콘의 관찰 사실로 대체하지 않았습니다. |

이 사례 모음은 사용자 선호 개선이나 각 설계 요소의 독립 효과를 입증하지 않습니다. 실제 생성 비교에서 조형 선택을 설명하는 데만 사용하고, QA 통과·AI 관찰·사용자 선택·플랫폼 검증을 별도 상태로 유지합니다.
