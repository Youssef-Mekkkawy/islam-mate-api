"""
Base Pydantic schemas shared across all modules.
Import these in any module's schemas.py to avoid repetition.
"""

from typing import Optional, Literal
from pydantic import BaseModel, Field, field_validator


class LangParam(BaseModel):
    """Standard lang query parameter — used by endpoints that accept ?lang=ar/en"""
    lang: Optional[Literal["ar", "en"]] = Field(
        default=None,
        description="Response language. 'ar' for Arabic, 'en' for English. Auto-detected from URL path if not provided.",
    )


class PaginationParams(BaseModel):
    """Standard pagination — page + limit"""
    page: int = Field(default=1, ge=1, description="Page number (starts at 1)")
    limit: int = Field(default=20, ge=1, le=100, description="Results per page (max 100)")

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.limit


class SearchParam(BaseModel):
    """Standard search query parameter"""
    q: str = Field(
        min_length=2,
        max_length=200,
        description="Search query (min 2 characters)",
    )

    @field_validator("q")
    @classmethod
    def strip_query(cls, v: str) -> str:
        return v.strip()


class CoordinatesParam(BaseModel):
    """Lat/long coordinates"""
    lat: float = Field(ge=-90, le=90, description="Latitude (-90 to 90)")
    lng: float = Field(ge=-180, le=180, description="Longitude (-180 to 180)")


class SurahParam(BaseModel):
    """Quran surah number"""
    surah: int = Field(ge=1, le=114, description="Surah number (1-114)")


class AyahParam(BaseModel):
    """Quran ayah number within a surah"""
    ayah: int = Field(ge=1, description="Ayah number within the surah")