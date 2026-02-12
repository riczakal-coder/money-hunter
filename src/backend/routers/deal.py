# ============================================================
# deal.py — Catch Deal API Router
# Maintainer: Young-cheol (Backend Engineer)
# ============================================================
# 핫딜/할인 정보 관련 API 엔드포인트를 정의합니다.
# 키워드: Alert, Fast, Discount
# ============================================================

from fastapi import APIRouter

router = APIRouter(
    prefix="/deal",
    tags=["🔥 Catch Deal"],
    responses={404: {"description": "Not found"}},
)


# ── 헬스 체크 ─────────────────────────────────────────────
@router.get("/")
async def deal_root():
    """Catch Deal 엔진 상태 확인."""
    return {
        "service": "Catch Deal",
        "status": "online",
        "description": "초특가 핫딜 헌팅 엔진",
    }


# ── 추후 확장용 엔드포인트 예시 ───────────────────────────
from sqlalchemy import select
from src.backend.database import AsyncSessionLocal
from src.backend.models import Deal


# ── 최신 핫딜 목록 조회 (DB 연동) ─────────────────────────
@router.get("/latest")
async def latest_deals(limit: int = 20):
    """최신 핫딜 목록을 조회합니다. (기본 20개)"""
    async with AsyncSessionLocal() as session:
        # 최신순 (id DESC) 정렬
        stmt = select(Deal).order_by(Deal.id.desc()).limit(limit)
        result = await session.execute(stmt)
        deals = result.scalars().all()
        
        return {
            "count": len(deals),
            "deals": deals,
        }
