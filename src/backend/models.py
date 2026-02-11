# ============================================================
# models.py — Money Hunter 데이터베이스 모델
# Maintainer: Young-cheol (Backend Engineer)
# ============================================================
# SQLAlchemy ORM 모델을 정의합니다.
# 이 파일의 클래스들이 실제 PostgreSQL 테이블로 매핑됩니다.
#
#   Deal   → 핫딜 정보 (Catch Deal 엔진)
#   Bottle → 주류 재고 (Catch Bottle 엔진)
# ============================================================

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  🔥 Catch Deal — 핫딜 정보 테이블
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class Deal(Base):
    """
    핫딜 게시글 정보를 저장하는 테이블.

    뽐뿌, 에펨코리아 등 커뮤니티에서 수집한 핫딜 데이터를 저장합니다.
    is_sent 플래그로 텔레그램 알림 발송 여부를 추적합니다.
    """

    __tablename__ = "deals"
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, autoincrement=True
    )
    site_name: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="출처 사이트 (예: ppomppu, fmkorea)"
    )
    title: Mapped[str] = mapped_column(
        String(500), nullable=False, comment="게시글 제목"
    )
    url: Mapped[str] = mapped_column(
        String(1000), nullable=False, unique=True, comment="게시글 링크 (중복 방지)"
    )
    price: Mapped[str | None] = mapped_column(
        String(100), nullable=True, comment="가격 정보 (예: 19,900원)"
    )
    is_sent: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, comment="텔레그램 알림 발송 여부"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        comment="데이터 수집 시간",
    )

    def __repr__(self) -> str:
        return f"<Deal(id={self.id}, site='{self.site_name}', title='{self.title[:30]}...')>"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  🥃 Catch Bottle — 주류 재고 테이블
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class Bottle(Base):
    """
    프리미엄 주류 재고 정보를 저장하는 테이블.

    편의점(CU, GS25), 대형마트(Costco) 등에서 수집한
    위스키/와인 재고 상태를 추적합니다.
    """

    __tablename__ = "bottles"
    __table_args__ = {'extend_existing': True}
    
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, autoincrement=True
    )
    merchant: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="판매처 (예: CU, GS25, Costco)"
    )
    product_name: Mapped[str] = mapped_column(
        String(300), nullable=False, comment="상품명 (예: 산토리 위스키 가쿠빈)"
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="unknown",
        comment="재고 상태 (in_stock / out_of_stock / unknown)",
    )
    last_checked: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        comment="마지막 재고 확인 시간",
    )

    def __repr__(self) -> str:
        return f"<Bottle(id={self.id}, merchant='{self.merchant}', product='{self.product_name[:30]}...')>"
