from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .base import db

class Notification(db.Model):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    bureau_id = Column(Integer, ForeignKey("bureaus.id"), nullable=True)
    role = Column(String(50), nullable=True) # e.g. "officer", "admin", "senior_authority"
    notification_type = Column(String(50), nullable=False) # "overlap_detected", "deadline_approaching", "case_overdue", "case_transferred", "status_updated"
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    related_complaint_id = Column(Integer, ForeignKey("complaints.id", ondelete="SET NULL"), nullable=True)
    related_case_link_id = Column(Integer, ForeignKey("case_links.id", ondelete="SET NULL"), nullable=True)
    read_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    user = relationship("User", back_populates="notifications")
    related_complaint = relationship("Complaint", foreign_keys=[related_complaint_id])
    related_case_link = relationship("CaseLink", foreign_keys=[related_case_link_id])

    @property
    def is_read(self) -> bool:
        return self.read_at is not None

    def mark_read(self):
        self.read_at = datetime.now(timezone.utc)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "bureau_id": self.bureau_id,
            "role": self.role,
            "notification_type": self.notification_type,
            "title": self.title,
            "message": self.message,
            "related_complaint_id": self.related_complaint_id,
            "related_case_number": self.related_complaint.case_number if self.related_complaint else None,
            "related_case_link_id": self.related_case_link_id,
            "is_read": self.is_read,
            "read_at": self.read_at.isoformat() if self.read_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
