from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class SearchRequestRecord(Base):
    __tablename__ = "search_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    request_id: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    status: Mapped[str] = mapped_column(String(40), default="planned")
    target_country: Mapped[str] = mapped_column(String(120), index=True)
    country_domain: Mapped[str | None] = mapped_column(String(40), nullable=True)
    product_name_tr: Mapped[str | None] = mapped_column(String(255), nullable=True)
    product_name_en: Mapped[str | None] = mapped_column(String(255), nullable=True)
    hs_code: Mapped[str | None] = mapped_column(String(80), nullable=True)
    oem_no: Mapped[str | None] = mapped_column(String(120), nullable=True)
    competitors: Mapped[str | None] = mapped_column(Text, nullable=True)
    related_sectors: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    results: Mapped[list["LeadResultRecord"]] = relationship(
        back_populates="search_request",
        cascade="all, delete-orphan",
    )


class LeadResultRecord(Base):
    __tablename__ = "lead_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    search_request_id: Mapped[int] = mapped_column(ForeignKey("search_requests.id"), index=True)
    company_name: Mapped[str] = mapped_column(String(255), index=True)
    country: Mapped[str] = mapped_column(String(120), index=True)
    city: Mapped[str | None] = mapped_column(String(120), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    website: Mapped[str | None] = mapped_column(String(500), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(80), nullable=True)
    source: Mapped[str] = mapped_column(String(120), index=True)
    source_type: Mapped[str] = mapped_column(String(80), index=True)
    matched_keyword: Mapped[str | None] = mapped_column(String(255), nullable=True)
    score: Mapped[int] = mapped_column(Integer)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_fit_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    suggested_contact_role: Mapped[str | None] = mapped_column(String(120), nullable=True)
    suggested_contact_emails: Mapped[str | None] = mapped_column(Text, nullable=True)
    suggested_email_subject: Mapped[str | None] = mapped_column(String(255), nullable=True)
    suggested_email_body: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    search_request: Mapped[SearchRequestRecord] = relationship(back_populates="results")
