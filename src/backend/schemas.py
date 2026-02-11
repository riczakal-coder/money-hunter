# ============================================================
# schemas.py — Money Hunter API 스키마 (Pydantic)
# Maintainer: Young-cheol (Backend Engineer)
# ============================================================
# API 요청(Request)과 응답(Response)의 데이터 형태를 정의합니다.
# FastAPI가 자동으로 검증, 직렬화, 문서화에 사용합니다.
# ============================================================

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  🔥 Catch Deal — 핫딜 스키마
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class DealCreate(BaseModel):
    """핫딜 생성 요청 스키마 (POST /deal)."""

    site_name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        examples=["ppomppu"],
        description="출처 사이트 이름",
    )
    title: str = Field(
        ...,
        min_length=1,
        max_length=500,
        examples=["[특가] 에어팟 프로 2 - 189,000원"],
        description="핫딜 게시글 제목",
    )
    url: str = Field(
        ...,
        max_length=1000,
        examples=["https://www.ppomppu.co.kr/zboard/view.php?id=ppomppu&no=12345"],
        description="게시글 URL",
    )
    price: str | None = Field(
        default=None,
        max_length=100,
        examples=["189,000원"],
        description="가격 정보 (선택)",
    )


class DealResponse(BaseModel):
    """핫딜 응답 스키마 (GET /deal)."""

    id: int
    site_name: str
    title: str
    url: str
    price: str | None = None
    is_sent: bool
    created_at: datetime

    # ORM 모드 활성화 — SQLAlchemy 모델 객체를 직접 변환 가능
    model_config = ConfigDict(from_attributes=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  🥃 Catch Bottle — 주류 스키마
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class BottleCreate(BaseModel):
    """주류 재고 생성 요청 스키마 (POST /bottle)."""

    merchant: str = Field(
        ...,
        min_length=1,
        max_length=100,
        examples=["CU"],
        description="판매처 이름",
    )
    product_name: str = Field(
        ...,
        min_length=1,
        max_length=300,
        examples=["산토리 위스키 가쿠빈 700ml"],
        description="상품명",
    )
    status: str = Field(
        default="unknown",
        max_length=20,
        examples=["in_stock"],
        description="재고 상태 (in_stock / out_of_stock / unknown)",
    )


class BottleResponse(BaseModel):
    """주류 재고 응답 스키마 (GET /bottle)."""

    id: int
    merchant: str
    product_name: str
    status: str
    last_checked: datetime

    # ORM 모드 활성화
    model_config = ConfigDict(from_attributes=True)
