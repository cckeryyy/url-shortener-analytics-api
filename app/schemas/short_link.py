import uuid
from datetime import datetime

from pydantic import BaseModel, HttpUrl, ConfigDict, field_validator


class ShortLinkCreate(BaseModel):
    original_url: HttpUrl
    custom_alias: str | None = None
    expires_at: datetime | None = None
    max_clicks: int | None = None

    @field_validator("custom_alias")
    @classmethod
    def validate_alias(cls, value: str | None) -> str | None:
        if value is None:
            return value
        if not value.isalnum():
            raise ValueError("custom_alias must contain only letters and digits")
        if not (3 <= len(value) <= 20):
            raise ValueError("custom_alias must be between 3 and 20 characters")
        return value


class ShortLinkOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    short_code: str
    original_url: str
    short_url: str
    is_active: bool
    expires_at: datetime | None
    max_clicks: int | None
    created_at: datetime
    click_count: int


class ShortLinkUpdate(BaseModel):
    is_active: bool | None = None
    expires_at: datetime | None = None
    max_clicks: int | None = None