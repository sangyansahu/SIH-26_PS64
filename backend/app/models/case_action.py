from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .base import db

class CaseAction(db.Model):
    __tablename__ = "case_actions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    complaint_id = Column(Integer, ForeignKey("complaints.id", ondelete="CASCADE"), nullable=False, index=True)
    action_type = Column(String(50), nullable=False)  # "status_change", "assignment", "bureau_transfer", "comment", "hearing", "disposition"
    description = Column(Text, nullable=False)
    old_status = Column(String(30), nullable=True)
    new_status = Column(String(30), nullable=True)
    old_bureau_id = Column(Integer, ForeignKey("bureaus.id"), nullable=True)
    new_bureau_id = Column(Integer, ForeignKey("bureaus.id"), nullable=True)
    performed_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    complaint = relationship("Complaint", back_populates="actions")
    performed_by = relationship("User", foreign_keys=[performed_by_id])
    old_bureau = relationship("Bureau", foreign_keys=[old_bureau_id])
    new_bureau = relationship("Bureau", foreign_keys=[new_bureau_id])

    def to_dict(self):
        return {
            "id": self.id,
            "complaint_id": self.complaint_id,
            "action_type": self.action_type,
            "description": self.description,
            "old_status": self.old_status,
            "new_status": self.new_status,
            "old_bureau_code": self.old_bureau.code if self.old_bureau else None,
            "new_bureau_code": self.new_bureau.code if self.new_bureau else None,
            "performed_by_name": self.performed_by.name if self.performed_by else "System",
            "performed_by_id": self.performed_by_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
