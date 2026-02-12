# ============================================================
# fmkorea.py — 에펨코리아 핫딜 게시판 크롤러
# Maintainer: Young-cheol (Backend Engineer)
# ============================================================
# FMKorea 핫딜 게시판에서 최신 핫딜을 수집하여
# PostgreSQL(deals 테이블)에 저장하고 텔레그램으로 알림합니다.
#
# 실행 방법 (프로젝트 루트에서):
#   cd src/backend && python -m crawlers.fmkorea
#
# HTML 구조 (2026년 2월 기준):
#   - 게시글 목록: div.fm_best_widget > li.li_best2_pop0
#   - 제목: h3.title > a 텍스트 (댓글수 [N] 제거)
#   - 링크: h3.title > a href → /숫자 → 도메인 붙이기
#   - 가격: div.hotdeal_info > span 중 "가격:" 포함 텍스트
# ============================================================

from __future__ import annotations

import logging
import re
import sys
from pathlib import Path

import httpx
from bs4 import BeautifulSoup

# ── sys.path 조정 ────────────────────────────────────────────
_BACKEND_DIR = str(Path(__file__).resolve().parent.parent)
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

from src.backend.config import settings
from src.backend.database import SessionLocal
from src.backend.models import Deal
from src.backend.notifier import (
    format_deal_message,
    get_smart_tags,
    send_message_sync,
    should_ban,
)

# ── 로깅 설정 ────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("fmkorea_crawler")

# ── 상수 정의 ────────────────────────────────────────────────
BOARD_URL = "https://www.fmkorea.com/hotdeal"
BASE_URL = "https://www.fmkorea.com"
SITE_NAME = "fmkorea"

# 펨코는 봇 차단이 심하므로 리얼한 브라우저 헤더 필수
# 펨코는 봇 차단이 심하므로 리얼한 브라우저 헤더 필수
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Referer": "https://www.fmkorea.com/",
    "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
}



def _clean_title(raw_title: str) -> str:
    """제목에서 댓글 수 [N] 제거."""
    return re.sub(r"\[\d+\]\s*$", "", raw_title).strip()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  메인 크롤링 함수
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def crawl_fmkorea() -> None:
    """
    에펨코리아 핫딜 게시판을 크롤링하여 DB에 저장합니다.

    1. httpx 동기 클라이언트로 페이지 요청 (리얼 헤더 포함)
    2. div.fm_best_widget > li.li_best2_pop0 파싱
    3. DB 중복 체크 후 신규 딜만 저장
    4. 신규 딜 발견 시 텔레그램 알림 발송
    """
    logger.info("=" * 60)
    logger.info("🚀 에펨코리아 핫딜 크롤링 시작")
    logger.info("=" * 60)

    # ── 텔레그램 설정 로드 ────────────────────────────────
    tg_token = settings.TELEGRAM_TOKEN
    tg_chat_id = settings.CHANNEL_ID_DEAL
    if not tg_token or not tg_chat_id:
        logger.warning("⚠️ TELEGRAM_TOKEN 또는 CHANNEL_ID_DEAL 미설정 → 알림 비활성")

    # ── 1. 페이지 요청 ────────────────────────────────────
    try:
        with httpx.Client(verify=False, timeout=15.0, follow_redirects=True) as client:
            res = client.get(BOARD_URL, headers=HEADERS)
    except httpx.RequestError as exc:
        logger.error("❌ 네트워크 에러: %s", exc)
        return

    if res.status_code != 200:
        logger.error("❌ HTTP %d 에러 (펨코 봇 차단일 수 있음)", res.status_code)
        return

    logger.info("✅ 페이지 수신 완료 — %d bytes", len(res.text))

    # ── 2. HTML 파싱 ──────────────────────────────────────
    soup = BeautifulSoup(res.text, "html.parser")

    # 게시글 목록: div.fm_best_widget > li.li_best2_pop0
    items = soup.select("div.fm_best_widget li.li_best2_pop0")
    logger.info("DEBUG: 찾은 게시글 수: %d개", len(items))

    if not items:
        logger.warning("⚠️ 게시글을 찾지 못했습니다. Cloudflare 차단 또는 셀렉터 변경 가능성.")
        return

    # ── 3. DB 저장 ────────────────────────────────────────
    db = SessionLocal()
    try:
        count = 0
        for li in items:
            # ── 제목 & 링크 ────────────────────────────
            h3 = li.select_one("h3.title")
            if not h3:
                continue

            a_tag = h3.select_one("a")
            if not a_tag:
                continue

            raw_title = a_tag.get_text(strip=True)
            title = _clean_title(raw_title)
            if not title:
                continue

            href = a_tag.get("href", "")
            # 링크 보정: /숫자 → 절대 URL
            if href.startswith("/"):
                link = f"{BASE_URL}{href}"
            elif href.startswith("http"):
                link = href
            else:
                link = f"{BASE_URL}/{href}"

            # ── 가격 찾기 ─────────────────────────────
            price = None
            info_div = li.select_one("div.hotdeal_info")
            if info_div:
                for span in info_div.select("span"):
                    span_text = span.get_text(strip=True)
                    if "가격:" in span_text or "가격 :" in span_text:
                        # "가격:83,075원" → "83,075원"
                        price = span_text.split(":", 1)[1].strip()
                        break

            # 가격이 없으면 제목에서 추출 시도
            if not price:
                price_match = re.search(r"(\d[\d,]*)\s*원", title)
                if price_match:
                    price = price_match.group(0)

            # ── 스마트 필터: 차단 키워드 체크 ─────────
            if should_ban(title, settings.BAN_KEYWORDS):
                continue

            # ── DB 중복 체크 ───────────────────────────
            existing = db.query(Deal).filter(Deal.url == link).first()
            if existing:
                logger.debug("중복 건너뜀: %s", title[:40])
                continue

            # ── 스마트 필터: 태그 부여 ─────────────────
            tags = get_smart_tags(title, settings.WATCH_KEYWORDS, settings.JACKPOT_KEYWORDS)

            # ── 신규 딜 저장 + 텔레그램 알림 ───────────
            sent = False
            if tg_token and tg_chat_id:
                msg = format_deal_message(title, price, link, site_label="펨코 핫딜", tags=tags)
                sent = send_message_sync(tg_token, tg_chat_id, msg)

            new_deal = Deal(
                site_name=SITE_NAME,
                title=title,
                url=link,
                price=price,
                is_sent=sent,
            )
            db.add(new_deal)
            count += 1
            logger.info("✅ 저장: %s (알림=%s)", title[:60], "발송" if sent else "미발송")

        # 한 번에 커밋 (배치)
        if count > 0:
            db.commit()
            logger.info("💾 DB 커밋 완료 — 신규 %d건 저장", count)
        else:
            logger.info("신규 딜 없음 (모두 중복)")

        logger.info("=" * 60)
        logger.info("🏁 펨코 수집 완료: %d건 저장됨", count)
        logger.info("=" * 60)

    except Exception as exc:
        db.rollback()
        logger.error("❌ DB 저장 중 에러: %s", exc, exc_info=True)

    finally:
        db.close()
        logger.info("DB 세션 닫힘")


# ── 진입점 ────────────────────────────────────────────────────
if __name__ == "__main__":
    crawl_fmkorea()
