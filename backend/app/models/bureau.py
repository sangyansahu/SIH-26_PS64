from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.orm import relationship
from .base import db

class Bureau(db.Model):
    __tablename__ = "bureaus"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(120), nullable=False)
    code = Column(String(20), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    users = relationship("User", back_populates="bureau", lazy="select")
    received_complaints = relationship("Complaint", foreign_keys="Complaint.receiving_bureau_id", back_populates="receiving_bureau", lazy="select")
    current_complaints = relationship("Complaint", foreign_keys="Complaint.current_bureau_id", back_populates="current_bureau", lazy="select")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "code": self.code,
            "description": self.description,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
