import uuid
import enum
from decimal import Decimal
from datetime import date
from sqlalchemy import String, Numeric, ForeignKey, Date, Text, Integer, Index
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.infrastructure.database.base import Base, TimestampMixin


class RatingCategory(str, enum.Enum):
    PERFORMANCE = "performance"
    TEAMWORK = "teamwork"
    INITIATIVE = "initiative"
    QUALITY = "quality"
    LEADERSHIP = "leadership"


class RatingMetric(Base, TimestampMixin):
    __tablename__ = "rating_metrics"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[RatingCategory] = mapped_column(SAEnum(RatingCategory), nullable=False)
    weight: Mapped[Decimal] = mapped_column(Numeric(4, 3), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(default=True)

    entries: Mapped[list["RatingEntry"]] = relationship(back_populates="metric")


class RatingEntry(Base, TimestampMixin):
    __tablename__ = "rating_entries"
    __table_args__ = (
        Index("ix_rating_employee_period", "employee_id", "period"),
        Index("ix_rating_period", "period"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    employee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False
    )
    reviewer_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("employees.id"), nullable=True
    )
    metric_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("rating_metrics.id"), nullable=False
    )
    period: Mapped[date] = mapped_column(Date, nullable=False)
    score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    category: Mapped[RatingCategory] = mapped_column(SAEnum(RatingCategory), nullable=False)
    comment: Mapped[str | None] = mapped_column(Text)

    employee: Mapped["Employee"] = relationship(
        back_populates="rating_entries",
        foreign_keys=[employee_id],
    )
    metric: Mapped["RatingMetric"] = relationship(back_populates="entries")


class RatingSnapshot(Base):
    __tablename__ = "rating_snapshots"
    __table_args__ = (
        Index("ix_snapshot_period_rank", "period", "rank"),
        Index("ix_snapshot_employee_period", "employee_id", "period", unique=True),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    employee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False
    )
    period: Mapped[date] = mapped_column(Date, nullable=False)
    total_score: Mapped[Decimal] = mapped_column(Numeric(6, 3))
    rank: Mapped[int] = mapped_column(Integer)
    department_rank: Mapped[int] = mapped_column(Integer)
    percentile: Mapped[Decimal] = mapped_column(Numeric(5, 2))
    delta_score: Mapped[Decimal | None] = mapped_column(Numeric(6, 3))
    delta_rank: Mapped[int | None] = mapped_column(Integer)

    employee: Mapped["Employee"] = relationship(back_populates="rating_snapshots")

