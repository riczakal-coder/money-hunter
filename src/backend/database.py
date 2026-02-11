# ============================================================
# database.py — Money Hunter DB 연결 모듈
# Maintainer: Young-cheol (Backend Engineer)
# ============================================================
# SQLAlchemy 비동기 엔진 및 세션 관리를 담당합니다.
# FastAPI 의존성 주입(Dependency Injection)으로 사용합니다.
# ============================================================

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from config import settings

# ── 1. AsyncEngine 생성 ──────────────────────────────────
# pool_pre_ping: 연결이 끊어진 경우 자동 재연결
# echo: DEBUG 모드일 때 SQL 쿼리 로그 출력
# connect_args: asyncpg 드라이버에 SSL 완전 비활성화
engine = create_async_engine(
    settings.DATABASE_URL + "?ssl=disable",
    pool_pre_ping=True,
    echo=settings.DEBUG,
    connect_args={
        "ssl": None,
        "server_settings": {"client_encoding": "utf8"},
    },
)

# ── 2. AsyncSession 팩토리 ───────────────────────────────
# expire_on_commit=False: 커밋 후에도 객체 속성에 접근 가능
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# ── 2-b. 동기 Engine & SessionLocal (크롤러 등 동기 스크립트용) ──
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

sync_engine = create_engine(
    settings.SYNC_DATABASE_URL,
    pool_pre_ping=True,
    echo=settings.DEBUG,
)

SessionLocal = sessionmaker(
    bind=sync_engine,
    class_=Session,
    expire_on_commit=False,
)


# ── 3. Base 클래스 (모든 ORM 모델의 부모) ────────────────
class Base(DeclarativeBase):
    """모든 ORM 모델이 상속받는 기본 클래스."""
    pass


# ── 4. 의존성 주입용 get_db 함수 ─────────────────────────
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI 의존성 주입(Depends)으로 사용하는 DB 세션 제공 함수.

    사용 예시:
        @router.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(Item))
            return result.scalars().all()
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
