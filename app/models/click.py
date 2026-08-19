import uuid
from datetime import datetime, timezone

from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, INET
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Click(Base):
    __tablename__ = "clicks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    clicked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    ip_address: Mapped[str | None] = mapped_column(INET, nullable=True)
    country: Mapped[str | None] = mapped_column(String(100), nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)

    device_type: Mapped[str | None] = mapped_column(String(20), nullable=True)
    browser: Mapped[str | None] = mapped_column(String(50), nullable=True)
    os: Mapped[str | None] = mapped_column(String(50), nullable=True)

    referrer: Mapped[str | None] = mapped_column(String(2048), nullable=True)

    link_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("short_links.id", ondelete="CASCADE"), nullable=False)
    link: Mapped["ShortLink"] = relationship(back_populates="clicks")