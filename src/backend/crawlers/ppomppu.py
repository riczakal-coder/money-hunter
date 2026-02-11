# ============================================================
# ppomppu.py — 뽐뿌 핫딜 게시판 크롤러
# Maintainer: Young-cheol (Backend Engineer)
# ============================================================
# 뽐뿌 핫딜 게시판(국내)에서 최신 핫딜을 수집하여
# PostgreSQL(deals 테이블)에 저장합니다.
#
# 실행 방법 (프로젝트 루트에서):
#   cd src/backend && python -m crawlers.ppomppu
#
# 핵심 전략:
#   - Library: httpx (동기) + bs4
#   - Encoding: res.encoding = "euc-kr" (필수!)
#   - Row: tr.baseList (2026년 기준 뽐뿌 신규 클래스)
#     ※ 구버전(tr.list0/list1)도 폴백으로 지원
#   - Title: td.title 내부 두 번째 a 태그 텍스트
#   - Link: a href → view.php로 시작하면 도메인 붙이기
#   - Price: 제목에서 정규식으로 추출 (XX,XXX원 패턴)
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

from config import settings                          # noqa: E402
from database import SessionLocal                    # noqa: E402
from models import Deal                              # noqa: E402
from notifier import (                               # noqa: E402
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
logger = logging.getLogger("ppomppu_crawler")

# ── 상수 정의 ────────────────────────────────────────────────
BOARD_URL = "https://www.ppomppu.co.kr/zboard/zboard.php?id=ppomppu"
BASE_URL = "https://www.ppomppu.co.kr/zboard/"
SITE_NAME = "ppomppu"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  메인 크롤링 함수
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def crawl_ppomppu() -> None:
    """
    뽐뿌 핫딜 게시판을 크롤링하여 DB에 저장합니다.

    1. httpx 동기 클라이언트로 페이지 요청 (verify=False)
    2. euc-kr 인코딩 강제 지정
    3. tr.baseList 행 파싱 (구버전 tr.list0/list1도 폴백)
    4. DB 중복 체크 후 신규 딜만 저장
    5. 신규 딜 발견 시 텔레그램 알림 발송
    """
    # ── 텔레그램 설정 로드 ────────────────────────────────
    tg_token = settings.TELEGRAM_TOKEN
    tg_chat_id = settings.CHANNEL_ID_DEAL
    if not tg_token or not tg_chat_id:
        logger.warning("⚠️ TELEGRAM_TOKEN 또는 CHANNEL_ID_DEAL 미설정 → 알림 비활성")
    logger.info("=" * 60)
    logger.info("🚀 뽐뿌 핫딜 크롤링 시작")
    logger.info("=" * 60)

    # ── 1. 페이지 요청 ────────────────────────────────────
    try:
        with httpx.Client(verify=False, timeout=15.0) as client:
            res = client.get(BOARD_URL, headers=HEADERS)
            res.encoding = "euc-kr"  # ⚡ 인코딩 강제 지정 (필수!)
    except httpx.RequestError as exc:
        logger.error("❌ 네트워크 에러: %s", exc)
        return

    if res.status_code != 200:
        logger.error("❌ HTTP %d 에러", res.status_code)
        return

    logger.info("✅ 페이지 수신 완료 — %d bytes", len(res.text))

    # ── 2. HTML 파싱 ──────────────────────────────────────
    soup = BeautifulSoup(res.text, "html.parser")

    # 신버전: tr.baseList  /  구버전 폴백: tr.list0, tr.list1
    rows = soup.select("tr.baseList")
    if not rows:
        rows = soup.select("tr.list0, tr.list1")
        logger.info("📌 구버전 셀렉터(list0/list1) 사용")

    logger.info("DEBUG: 찾은 게시글 수: %d개", len(rows))

    if not rows:
        logger.warning("⚠️ 게시글을 찾지 못했습니다. 선택자를 확인하세요.")
        return

    # ── 3. DB 저장 ────────────────────────────────────────
    db = SessionLocal()
    try:
        count = 0
        for row in rows:
            # ── 제목 & 링크 찾기 ───────────────────────
            # 신버전 구조: td.title 안에 a 태그가 2개
            #   첫 번째 a: href만 있고 텍스트 없음 (썸네일 등)
            #   두 번째 a: 실제 제목 텍스트 포함
            title_td = row.select_one("td.title")
            if title_td:
                # td.title 내 모든 a 태그 중 텍스트가 있는 것을 찾기
                a_tags = title_td.select("a")
                title = None
                link = None
                for a in a_tags:
                    text = a.get_text(strip=True)
                    href = a.get("href", "")
                    if text and ("view.php" in href or "zboard.php" in href):
                        title = text
                        link = href
                        break

                if not title:
                    # 폴백: font.list_title 시도 (구버전)
                    ft = row.select_one("font.list_title")
                    if ft:
                        title = ft.get_text(strip=True)
                    # 그래도 없으면 아무 a 태그
                    if not title and a_tags:
                        for a in a_tags:
                            t = a.get_text(strip=True)
                            if t:
                                title = t
                                link = a.get("href", "")
                                break
            else:
                # 구버전 구조 폴백
                title_tag = row.select_one("font.list_title")
                if not title_tag:
                    title_tag = row.select_one("a")
                if not title_tag:
                    continue
                title = title_tag.get_text(strip=True)
                link_tag = row.select_one("a[href]")
                link = link_tag.get("href", "") if link_tag else None

            if not title or not link:
                continue

            # ── 링크 보정 ──────────────────────────────
            if link.startswith("view.php") or link.startswith("zboard.php"):
                link = f"{BASE_URL}{link}"
            elif link.startswith("/"):
                link = f"https://www.ppomppu.co.kr{link}"

            # ── 가격 찾기 ─────────────────────────────
            price = None

            # 방법1: td.eng.list_vspace (구버전)
            price_tag = row.select_one("td.eng.list_vspace")
            if price_tag:
                price = price_tag.get_text(strip=True)

            # 방법2: 제목에서 가격 패턴 추출
            if not price:
                price_match = re.search(r"[\(\[]?\s*(\d[\d,]*)\s*원", title)
                if price_match:
                    price = price_match.group(0).strip("([]) ")

            # ── 스마트 필터: 차단 키워드 체크 ─────────
            if should_ban(title, settings.BAN_KEYWORDS):
                continue

            # ── DB 중복 체크 ───────────────────────
            existing = db.query(Deal).filter(Deal.url == link).first()
            if existing:
                logger.debug("중복 건너뛰: %s", title[:40])
                continue

            # ── 스마트 필터: 태그 부여 ─────────────
            tags = get_smart_tags(title, settings.WATCH_KEYWORDS, settings.JACKPOT_KEYWORDS)

            # ── 신규 딜 저장 ───────────────────────────
            # 텔레그램 알림 발송 (INSERT 시점에만!)
            sent = False
            if tg_token and tg_chat_id:
                msg = format_deal_message(title, price, link, site_label="뽐뿌 핫딜", tags=tags)
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
        logger.info("🏁 수집 완료: %d건 저장됨", count)
        logger.info("=" * 60)

    except Exception as exc:
        db.rollback()
        logger.error("❌ DB 저장 중 에러: %s", exc, exc_info=True)

    finally:
        db.close()
        logger.info("DB 세션 닫힘")


# ── 진입점 ────────────────────────────────────────────────────
if __name__ == "__main__":
    crawl_ppomppu()
