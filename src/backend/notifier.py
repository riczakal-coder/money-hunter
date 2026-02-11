# ============================================================
# notifier.py — 텔레그램 알림 발송 모듈
# Maintainer: Young-cheol (Backend Engineer)
# ============================================================
# 텔레그램 Bot API를 통해 핫딜 알림, 주류 재고 알림 등을
# 사용자에게 발송합니다.
#
# 사용법:
#   동기 (크롤러 등):
#     from notifier import send_message_sync
#     send_message_sync(token, chat_id, "메시지")
#
#   비동기 (FastAPI 등):
#     from notifier import send_message_async
#     await send_message_async(token, chat_id, "메시지")
# ============================================================

from __future__ import annotations

import logging

import httpx

logger = logging.getLogger("notifier")

# ── 텔레그램 Bot API 엔드포인트 ──────────────────────────────
TELEGRAM_API = "https://api.telegram.org/bot{token}/sendMessage"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  동기 버전 (크롤러, 스크립트용)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def send_message_sync(
    token: str,
    chat_id: str,
    message: str,
    *,
    parse_mode: str = "HTML",
    disable_web_page_preview: bool = True,
) -> bool:
    """
    텔레그램 메시지를 동기적으로 발송합니다.

    Args:
        token: 텔레그램 봇 토큰
        chat_id: 메시지를 받을 채팅/채널 ID
        message: 발송할 메시지 본문
        parse_mode: 메시지 파싱 모드 (HTML / Markdown)
        disable_web_page_preview: 링크 미리보기 비활성화

    Returns:
        True: 발송 성공
        False: 발송 실패 (에러 로그 남김, 프로그램은 안 멈춤)
    """
    if not token or not chat_id:
        logger.warning("⚠️ 텔레그램 토큰 또는 chat_id가 비어있습니다. 알림 건너뜀.")
        return False

    url = TELEGRAM_API.format(token=token)
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": parse_mode,
        "disable_web_page_preview": disable_web_page_preview,
    }

    try:
        with httpx.Client(timeout=10.0) as client:
            res = client.post(url, json=payload)

        if res.status_code == 200 and res.json().get("ok"):
            logger.info("📨 텔레그램 발송 성공 → chat_id=%s", chat_id)
            return True
        else:
            logger.error(
                "❌ 텔레그램 발송 실패 — HTTP %d, 응답: %s",
                res.status_code,
                res.text[:200],
            )
            return False

    except httpx.RequestError as exc:
        logger.error("❌ 텔레그램 네트워크 에러: %s", exc)
        return False
    except Exception as exc:
        logger.error("❌ 텔레그램 발송 중 예외: %s", exc)
        return False


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  비동기 버전 (FastAPI, 비동기 스크립트용)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def send_message_async(
    token: str,
    chat_id: str,
    message: str,
    *,
    parse_mode: str = "HTML",
    disable_web_page_preview: bool = True,
) -> bool:
    """
    텔레그램 메시지를 비동기적으로 발송합니다.

    사용법 (FastAPI 등):
        await send_message_async(token, chat_id, "메시지")

    Args/Returns: send_message_sync와 동일
    """
    if not token or not chat_id:
        logger.warning("⚠️ 텔레그램 토큰 또는 chat_id가 비어있습니다. 알림 건너뜀.")
        return False

    url = TELEGRAM_API.format(token=token)
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": parse_mode,
        "disable_web_page_preview": disable_web_page_preview,
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.post(url, json=payload)

        if res.status_code == 200 and res.json().get("ok"):
            logger.info("📨 텔레그램 발송 성공 → chat_id=%s", chat_id)
            return True
        else:
            logger.error(
                "❌ 텔레그램 발송 실패 — HTTP %d, 응답: %s",
                res.status_code,
                res.text[:200],
            )
            return False

    except httpx.RequestError as exc:
        logger.error("❌ 텔레그램 네트워크 에러: %s", exc)
        return False
    except Exception as exc:
        logger.error("❌ 텔레그램 발송 중 예외: %s", exc)
        return False


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  핫딜 알림 메시지 포매터
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def format_deal_message(
    title: str,
    price: str | None,
    url: str,
    *,
    site_label: str = "뽐뿌 핫딜",
    tags: list[str] | None = None,
) -> str:
    """
    핫딜 정보를 텔레그램 알림 메시지 포맷으로 변환합니다.

    Args:
        site_label: 사이트 구분 라벨 (예: "뽐뿌 핫딜", "펨코 핫딜")
        tags: 스마트 필터 태그 리스트 (예: ["❤️관심", "🔥대박"])
    """
    price_text = price if price else "정보 없음"
    tag_line = " ".join(f"[{t}]" for t in tags) if tags else ""
    header = f"[🔥 {site_label}]"
    if tag_line:
        header = f"{header} {tag_line}"

    return (
        f"{header}\n"
        f"제목: {title}\n"
        f"가격: {price_text}\n"
        f"링크: {url}"
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  스마트 필터 엔진
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def should_ban(title: str, ban_keywords: list[str]) -> bool:
    """
    제목에 차단 키워드가 포함되어 있으면 True를 반환합니다.
    True인 경우 해당 게시글은 수집하지 않습니다.
    """
    title_lower = title.lower()
    for kw in ban_keywords:
        if kw.lower() in title_lower:
            logger.info("🚫 차단 필터: '%s' 포함 → %s", kw, title[:40])
            return True
    return False


def get_smart_tags(
    title: str,
    watch_keywords: list[str],
    jackpot_keywords: list[str],
) -> list[str]:
    """
    제목을 분석하여 해당하는 태그 리스트를 반환합니다.

    - 대박 키워드 매칭: "🔥대박" 태그
    - 관심 키워드 매칭: "❤️관심" 태그
    - 둘 다 해당 가능 (태그 중복 허용)

    Returns:
        ["🔥대박"], ["❤️관심"], ["🔥대박", "❤️관심"], 또는 []
    """
    tags: list[str] = []
    title_lower = title.lower()

    # 대박 키워드 체크 (우선순위 높음)
    for kw in jackpot_keywords:
        if kw.lower() in title_lower:
            tags.append("🔥대박")
            logger.info("💥 대박 키워드 감지: '%s' → %s", kw, title[:40])
            break  # 한 번만

    # 관심 키워드 체크
    for kw in watch_keywords:
        if kw.lower() in title_lower:
            tags.append("❤️관심")
            logger.info("💖 관심 키워드 감지: '%s' → %s", kw, title[:40])
            break  # 한 번만

    return tags
