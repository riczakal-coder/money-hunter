# ============================================================
# stitch_server.py — Stitch Design MCP Server
# Code Name: Stitch (Creative Director & MCP Server Manager)
# Project: Money Hunter
# ============================================================
# 두 가지 브랜드의 디자인 리소스를 MCP 도구(Tool)로 제공하는 서버.
#   - Catch Bottle : 프리미엄, 럭셔리 테마
#   - Catch Deal   : 스피디, 할인 알림 테마
# ============================================================

from mcp.server.fastmcp import FastMCP
import json
import re
from typing import Literal

# ── MCP 서버 인스턴스 ───────────────────────────────────────
mcp = FastMCP(
    "Stitch Design Service",
    description=(
        "Money Hunter 프로젝트의 크리에이티브 디렉터 Stitch가 운영하는 "
        "디자인 리소스 MCP 서버입니다. "
        "브랜드 컬러, 폰트 가이드, 로고 프롬프트, UI 리뷰 기능을 제공합니다."
    ),
)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  내부 데이터: 디자인 시스템 정의
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DESIGN_SYSTEMS: dict[str, dict] = {
    "bottle": {
        "service_name": "Catch Bottle",
        "concept": "Premium / Luxury / Exclusive / Night",
        "colors": {
            "primary": {"name": "Royal Gold", "hex": "#D4AF37"},
            "background": {"name": "Obsidian Black", "hex": "#121212"},
            "surface": {"name": "Dark Charcoal", "hex": "#1E1E1E"},
            "text_primary": {"name": "Champagne White", "hex": "#F5F0E8"},
            "text_secondary": {"name": "Muted Gold", "hex": "#B8963E"},
            "accent": {"name": "Amber Glow", "hex": "#FFBF00"},
            "border": {"name": "Soft Gold", "hex": "#A08630"},
            "error": {"name": "Ruby Red", "hex": "#C0392B"},
            "success": {"name": "Emerald", "hex": "#2ECC71"},
        },
        "typography": {
            "font_family_primary": "'Playfair Display', 'Noto Serif KR', Georgia, serif",
            "font_family_secondary": "'Cormorant Garamond', 'Nanum Myeongjo', serif",
            "font_family_mono": "'JetBrains Mono', 'D2Coding', monospace",
            "heading_weight": "700",
            "body_weight": "400",
            "letter_spacing": "0.03em",
            "line_height": "1.7",
        },
        "style_guide": {
            "border_radius": "2px",
            "shadow": "0 4px 24px rgba(212, 175, 55, 0.15)",
            "gradient": "linear-gradient(135deg, #D4AF37 0%, #B8963E 50%, #8B7029 100%)",
            "hover_effect": "box-shadow 0.3s ease, transform 0.2s ease",
            "animation": "subtle fade-in, gold shimmer on hover",
            "icon_style": "outlined, thin-stroke, elegant",
        },
    },
    "deal": {
        "service_name": "Catch Deal",
        "concept": "Alert / Fast / Discount / Speedy",
        "colors": {
            "primary": {"name": "Vivid Red", "hex": "#FF4500"},
            "background": {"name": "Clean White", "hex": "#FFFFFF"},
            "surface": {"name": "Light Gray", "hex": "#F8F9FA"},
            "text_primary": {"name": "Dark Navy", "hex": "#1A1A2E"},
            "text_secondary": {"name": "Steel Gray", "hex": "#6C757D"},
            "accent": {"name": "Hot Orange", "hex": "#FF6B35"},
            "border": {"name": "Soft Border", "hex": "#DEE2E6"},
            "error": {"name": "Danger Red", "hex": "#DC3545"},
            "success": {"name": "Fresh Green", "hex": "#28A745"},
            "badge_highlight": {"name": "Flash Yellow", "hex": "#FFD700"},
        },
        "typography": {
            "font_family_primary": "'Inter', 'Noto Sans KR', 'Pretendard', sans-serif",
            "font_family_secondary": "'Outfit', 'Spoqa Han Sans Neo', sans-serif",
            "font_family_mono": "'Fira Code', 'D2Coding', monospace",
            "heading_weight": "800",
            "body_weight": "400",
            "letter_spacing": "-0.01em",
            "line_height": "1.5",
        },
        "style_guide": {
            "border_radius": "12px",
            "shadow": "0 2px 12px rgba(255, 69, 0, 0.12)",
            "gradient": "linear-gradient(135deg, #FF4500 0%, #FF6B35 50%, #FF8C42 100%)",
            "hover_effect": "scale(1.03), background-color shift 0.15s",
            "animation": "bounce-in, pulse on new deal, shake on alert",
            "icon_style": "filled, bold, rounded",
        },
    },
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Tool 1: get_design_system
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@mcp.tool()
def get_design_system(service_type: str) -> str:
    """
    서비스 타입에 따른 전체 디자인 시스템을 JSON으로 반환합니다.

    Args:
        service_type: 'bottle' (Catch Bottle, 프리미엄) 또는
                      'deal' (Catch Deal, 스피디) 중 하나.

    Returns:
        해당 서비스의 컬러 팔레트, 타이포그래피, 스타일 가이드가 포함된
        JSON 문자열. 잘못된 타입 입력 시 에러 메시지 반환.
    """
    key = service_type.strip().lower()

    if key not in DESIGN_SYSTEMS:
        available = ", ".join(f"'{k}'" for k in DESIGN_SYSTEMS)
        return json.dumps(
            {
                "error": True,
                "message": (
                    f"알 수 없는 서비스 타입: '{service_type}'. "
                    f"사용 가능한 옵션: {available}"
                ),
            },
            ensure_ascii=False,
            indent=2,
        )

    system = DESIGN_SYSTEMS[key]
    return json.dumps(
        {
            "service_name": system["service_name"],
            "concept": system["concept"],
            "colors": system["colors"],
            "typography": system["typography"],
            "style_guide": system["style_guide"],
        },
        ensure_ascii=False,
        indent=2,
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Tool 2: generate_logo_prompt
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
LOGO_TEMPLATES: dict[str, dict] = {
    "catch bottle": {
        "style": "luxury minimalist",
        "mood": "exclusive, sophisticated, nightlife",
        "palette": "deep black background with metallic gold accents",
        "typography_hint": "elegant serif lettermark",
        "motifs": [
            "premium wine bottle silhouette",
            "golden crown icon",
            "champagne bubbles abstract pattern",
            "diamond-cut facets",
        ],
    },
    "catch deal": {
        "style": "bold modern flat",
        "mood": "energetic, urgent, exciting, deal-hunting",
        "palette": "vivid red-orange on clean white",
        "typography_hint": "heavy sans-serif wordmark with speed lines",
        "motifs": [
            "lightning bolt inside a price tag",
            "shopping cart with rocket exhaust",
            "alarm bell with discount percentage",
            "crosshair target on a deal badge",
        ],
    },
}


@mcp.tool()
def generate_logo_prompt(service_name: str) -> str:
    """
    서비스 이름을 입력받아 AI 이미지 생성기(DALL-E, Midjourney 등)에
    바로 사용할 수 있는 고퀄리티 영문 로고 프롬프트를 생성합니다.

    Args:
        service_name: 서비스 이름. 예: 'Catch Bottle', 'Catch Deal'

    Returns:
        AI 이미지 생성기에 넣을 수 있는 영문 프롬프트 문자열.
        매칭되는 서비스가 없으면 범용 프롬프트를 생성합니다.
    """
    key = service_name.strip().lower()
    template = LOGO_TEMPLATES.get(key)

    if template:
        motif_options = " | ".join(template["motifs"])
        prompt = (
            f"Design a professional logo for '{service_name}'. "
            f"Style: {template['style']}. "
            f"Mood: {template['mood']}. "
            f"Color palette: {template['palette']}. "
            f"Typography: {template['typography_hint']}. "
            f"Suggested motifs (pick one or combine): {motif_options}. "
            f"The logo must work on both light and dark backgrounds. "
            f"Render in high resolution, vector-quality, centered composition, "
            f"no text artifacts, clean edges, suitable for app icon and web header. "
            f"Aspect ratio 1:1, transparent background preferred."
        )
    else:
        # 매칭 안 되면 범용 프롬프트 생성
        prompt = (
            f"Design a sleek, modern, professional logo for '{service_name}'. "
            f"Style: clean minimalist with a tech-forward aesthetic. "
            f"Use a balanced color palette that conveys trust and innovation. "
            f"The logo should include a subtle icon element alongside a refined wordmark. "
            f"High resolution, vector-quality, centered composition, "
            f"no text artifacts, clean edges, suitable for app icon and web header. "
            f"Aspect ratio 1:1, transparent background preferred."
        )

    return json.dumps(
        {
            "service_name": service_name,
            "prompt": prompt,
            "usage_tip": (
                "이 프롬프트를 DALL-E 3, Midjourney v6, 또는 "
                "Stable Diffusion XL에 입력하세요. "
                "필요에 따라 '--ar 1:1 --style raw' (Midjourney) 등 "
                "플랫폼별 파라미터를 추가하세요."
            ),
        },
        ensure_ascii=False,
        indent=2,
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Tool 3: review_ui_component
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 검사 규칙 정의
_REVIEW_RULES: list[dict] = [
    # ── 접근성(A11y) ──
    {
        "id": "A11Y_IMG_ALT",
        "severity": "error",
        "pattern": re.compile(r"<img\b(?![^>]*\balt\s*=)", re.IGNORECASE),
        "message": "🖼️ <img> 태그에 `alt` 속성이 없습니다. 접근성을 위해 반드시 추가하세요.",
    },
    {
        "id": "A11Y_BUTTON_EMPTY",
        "severity": "warning",
        "pattern": re.compile(
            r"<button[^>]*>\s*</button>", re.IGNORECASE
        ),
        "message": "🔘 빈 <button> 태그가 있습니다. aria-label 또는 텍스트를 추가하세요.",
    },
    {
        "id": "A11Y_ANCHOR_EMPTY",
        "severity": "warning",
        "pattern": re.compile(r"<a\b[^>]*>\s*</a>", re.IGNORECASE),
        "message": "🔗 빈 <a> 태그가 있습니다. 링크 텍스트를 추가하세요.",
    },
    # ── 스타일링 ──
    {
        "id": "STYLE_INLINE",
        "severity": "info",
        "pattern": re.compile(r'\bstyle\s*=\s*"', re.IGNORECASE),
        "message": (
            "🎨 인라인 style 속성이 발견되었습니다. "
            "유지보수를 위해 CSS 클래스 또는 Tailwind 유틸리티로 전환을 권장합니다."
        ),
    },
    {
        "id": "STYLE_NO_CLASS",
        "severity": "info",
        "pattern": re.compile(
            r"<(div|section|main|header|footer|article|aside)\b(?![^>]*\bclass\s*=)",
            re.IGNORECASE,
        ),
        "message": (
            "📦 주요 시맨틱/레이아웃 태그에 class가 없습니다. "
            "디자인 시스템 클래스를 적용하세요."
        ),
    },
    # ── Tailwind 검사 ──
    {
        "id": "TW_RESPONSIVE",
        "severity": "info",
        "pattern": re.compile(r"\b(sm:|md:|lg:|xl:|2xl:)", re.IGNORECASE),
        "message": "📱 Tailwind 반응형 접두사가 감지되었습니다. 모든 브레이크포인트를 검증하세요.",
    },
    {
        "id": "TW_DARK_MODE",
        "severity": "info",
        "pattern": re.compile(r"\bdark:", re.IGNORECASE),
        "message": "🌙 Tailwind dark: 클래스가 사용되었습니다. 다크모드 전환 테스트를 권장합니다.",
    },
    # ── 성능 ──
    {
        "id": "PERF_LARGE_BUNDLE",
        "severity": "warning",
        "pattern": re.compile(
            r'<script\b[^>]*src\s*=\s*"[^"]*\b(jquery|lodash|moment)\b',
            re.IGNORECASE,
        ),
        "message": (
            "⚡ 대형 번들 라이브러리(jQuery/Lodash/Moment)가 직접 로드되고 있습니다. "
            "트리쉐이킹이 가능한 대안을 고려하세요."
        ),
    },
    # ── 시맨틱 HTML ──
    {
        "id": "SEM_HEADING_ORDER",
        "severity": "warning",
        "pattern": re.compile(r"<h[3-6]\b", re.IGNORECASE),
        "message": (
            "📝 h3~h6 헤딩이 사용되었습니다. h1→h2→h3… 순서가 올바른지 확인하세요."
        ),
    },
]

# 브랜드 색상 매핑 (HTML 내에서 올바른 브랜드 색상 사용 여부 체크)
_BRAND_COLORS = {
    "bottle": {"#D4AF37", "#121212", "#1E1E1E", "#F5F0E8", "#B8963E", "#FFBF00"},
    "deal": {"#FF4500", "#FFFFFF", "#F8F9FA", "#1A1A2E", "#6C757D", "#FF6B35", "#FFD700"},
}


@mcp.tool()
def review_ui_component(html_code: str) -> str:
    """
    입력된 HTML 코드 스니펫을 디자인 관점에서 리뷰합니다.

    검사 항목:
    - 접근성 (alt 속성, 빈 버튼/링크)
    - 스타일링 (인라인 스타일, 클래스 누락)
    - Tailwind CSS 사용 패턴 (반응형, 다크모드)
    - 성능 (대형 번들 라이브러리)
    - 시맨틱 HTML (헤딩 순서)
    - 브랜드 컬러 일치 여부

    Args:
        html_code: 리뷰할 HTML 코드 문자열.

    Returns:
        리뷰 결과를 담은 JSON 문자열. issues 배열과 summary 포함.
    """
    issues: list[dict] = []

    # ── 규칙 기반 검사 ──
    for rule in _REVIEW_RULES:
        matches = rule["pattern"].findall(html_code)
        if matches:
            issues.append(
                {
                    "rule_id": rule["id"],
                    "severity": rule["severity"],
                    "message": rule["message"],
                    "occurrences": len(matches),
                }
            )

    # ── 브랜드 컬러 연관 검사 ──
    hex_colors_in_code = set(
        re.findall(r"#[0-9A-Fa-f]{6}\b", html_code)
    )
    hex_colors_upper = {c.upper() for c in hex_colors_in_code}

    if hex_colors_upper:
        # 어떤 브랜드에 속하는지 판별
        bottle_match = hex_colors_upper & _BRAND_COLORS["bottle"]
        deal_match = hex_colors_upper & _BRAND_COLORS["deal"]
        unknown_colors = hex_colors_upper - _BRAND_COLORS["bottle"] - _BRAND_COLORS["deal"]

        if bottle_match and deal_match:
            issues.append(
                {
                    "rule_id": "BRAND_MIX",
                    "severity": "warning",
                    "message": (
                        "⚠️ Catch Bottle과 Catch Deal의 브랜드 컬러가 혼용되었습니다. "
                        "하나의 컴포넌트에는 한 브랜드의 컬러만 사용하세요."
                    ),
                    "details": {
                        "bottle_colors_found": sorted(bottle_match),
                        "deal_colors_found": sorted(deal_match),
                    },
                }
            )

        if unknown_colors:
            issues.append(
                {
                    "rule_id": "BRAND_UNKNOWN_COLOR",
                    "severity": "info",
                    "message": (
                        "🎨 디자인 시스템에 정의되지 않은 컬러가 사용되었습니다. "
                        "의도된 사용인지 확인하세요."
                    ),
                    "details": {"unknown_colors": sorted(unknown_colors)},
                }
            )

    # ── 요약 생성 ──
    error_count = sum(1 for i in issues if i["severity"] == "error")
    warning_count = sum(1 for i in issues if i["severity"] == "warning")
    info_count = sum(1 for i in issues if i["severity"] == "info")

    if error_count > 0:
        grade = "❌ 수정 필요"
    elif warning_count > 0:
        grade = "⚠️ 개선 권장"
    elif info_count > 0:
        grade = "💡 참고사항 있음"
    else:
        grade = "✅ 완벽합니다!"

    summary = {
        "grade": grade,
        "total_issues": len(issues),
        "errors": error_count,
        "warnings": warning_count,
        "info": info_count,
    }

    return json.dumps(
        {"summary": summary, "issues": issues},
        ensure_ascii=False,
        indent=2,
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  서버 실행
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if __name__ == "__main__":
    mcp.run()