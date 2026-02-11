# ============================================================
# main.py — Money Hunter Backend Server
# Maintainer: Young-cheol (Backend Engineer)
# ============================================================
# FastAPI 기반 메인 애플리케이션.
# 두 개의 트윈 엔진(Catch Bottle, Catch Deal)을 라우터로 등록합니다.
# APScheduler로 크롤러를 주기적으로 자동 실행합니다.
# ============================================================

import logging
from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy import text

from src.backend.config import settings
from crawlers.fmkorea import crawl_fmkorea
from crawlers.ppomppu import crawl_ppomppu
from database import AsyncSessionLocal, Base, engine
from routers import bottle, deal
import models  # noqa: F401 — Base.metadata에 모델 등록용

# ── 로깅 설정 ─────────────────────────────────────────────
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s │ %(levelname)-8s │ %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("money_hunter")

# ── APScheduler 인스턴스 (전역) ────────────────────────────
scheduler = AsyncIOScheduler()


# ── Lifespan (서버 시작/종료 이벤트) ──────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """서버 기동/종료 시 실행되는 라이프사이클 핸들러."""
    # ▶ STARTUP
    logger.info("=" * 50)
    logger.info("🚀 Money Hunter Server Started!")
    logger.info(f"   Project : {settings.PROJECT_NAME} v{settings.VERSION}")
    logger.info(f"   Debug   : {settings.DEBUG}")
    logger.info(f"   Host    : {settings.HOST}:{settings.PORT}")
    logger.info(f"   DB      : {settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}")
    logger.info("=" * 50)

    # ── DB 테이블 자동 생성 ──
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("✅ Tables created! (deals, bottles)")

    # ── 스케줄러 시작 ──────────────────────────────────
    # 동기 크롤러 함수들 → APScheduler가 ThreadPoolExecutor에서
    # 자동 실행하므로 이벤트 루프를 블로킹하지 않음
    scheduler.add_job(
        crawl_ppomppu,
        trigger="interval",
        seconds=60,
        id="ppomppu_crawler",
        name="뽐뿌 핫딜 크롤러 (60초 간격)",
        replace_existing=True,
    )
    scheduler.add_job(
        crawl_fmkorea,
        trigger="interval",
        seconds=60,
        id="fmkorea_crawler",
        name="펨코 핫딜 크롤러 (60초 간격, 30초 시차)",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("⏰ 스케줄러 시작됨 — 뽐뿌/펨코 크롤러 60초 간격 자동 실행")

    yield  # ← 여기서 서버가 요청을 처리합니다

    # ◼ SHUTDOWN
    scheduler.shutdown(wait=False)
    logger.info("⏰ 스케줄러 종료됨")
    logger.info("👋 Money Hunter Server Shutting Down...")


# ── FastAPI 앱 인스턴스 ───────────────────────────────────
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=(
        "Money Hunter 백엔드 API 서버.\n\n"
        "- 🥃 **Catch Bottle** — 프리미엄 위스키 & 와인 헌팅\n"
        "- 🔥 **Catch Deal** — 초특가 핫딜 헌팅"
    ),
    lifespan=lifespan,
)


# ── 라우터 등록 (트윈 엔진) ───────────────────────────────
app.include_router(bottle.router)
app.include_router(deal.router)


# ── 헬스 체크 (루트 엔드포인트) ───────────────────────────
@app.get("/", tags=["🏠 General"])
async def root():
    """서버 상태 확인용 헬스 체크 엔드포인트."""
    return {
        "status": "ok",
        "engine": "Money Hunter",
    }


# ── DB 연결 테스트 엔드포인트 ─────────────────────────────
@app.get("/db-check", tags=["🏠 General"])
async def db_check():
    """PostgreSQL 연결 상태를 확인합니다. SELECT 1 쿼리를 실행합니다."""
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(text("SELECT 1"))
            value = result.scalar()
            if value == 1:
                return {
                    "status": "ok",
                    "message": "DB Connected!",
                    "database": settings.DB_NAME,
                    "host": settings.DB_HOST,
                }
    except Exception as e:
        logger.error(f"❌ DB 연결 실패: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "DB 연결 실패",
                "detail": str(e),
            },
        )
