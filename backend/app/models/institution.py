from datetime import datetime, timezone
import json
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from .base import db

class Institution(db.Model):
    __tablename__ = "institutions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    institution_code = Column(String(50), unique=True, nullable=False, index=True) # e.g. AICTE Permanent ID "1-10293847"
    name = Column(String(255), nullable=False, index=True)
    aliases = Column(Text, nullable=True)  # JSON array of known aliases/abbreviations
    institution_type = Column(String(100), nullable=False) # e.g. "Engineering & Technology", "Management"
    state = Column(String(100), nullable=False, index=True)
    district = Column(String(100), nullable=True)
    address = Column(Text, nullable=True)
    pincode = Column(String(20), nullable=True)
    website = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    complaints = relationship("Complaint", back_populates="institution", lazy="select", cascade="all")

    @property
    def alias_list(self):
        if not self.aliases:
            return []
        try:
            return json.loads(self.aliases)
        except Exception:
            return [a.strip() for a in self.aliases.split(",") if a.strip()]

    def set_aliases(self, aliases_list):
        if isinstance(aliases_list, list):
            self.aliases = json.dumps(aliases_list)
        else:
            self.aliases = json.dumps([str(aliases_list)])

    def to_dict(self, include_stats=False):
        data = {
            "id": self.id,
            "institution_code": self.institution_code,
            "name": self.name,
            "aliases": self.alias_list,
            "institution_type": self.institution_type,
            "state": self.state,
            "district": self.district,
            "address": self.address,
            "pincode": self.pincode,
            "website": self.website,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_stats:
            complaints = self.complaints or []
            data["total_complaints"] = len(complaints)
            data["open_complaints"] = sum(1 for c in complaints if c.status not in ("Disposed", "Closed"))
            data["disposed_complaints"] = sum(1 for c in complaints if c.status in ("Disposed", "Closed"))
            data["escalated_complaints"] = sum(1 for c in complaints if c.status == "Escalated")
            data["bureaus_involved"] = list({c.current_bureau.code for c in complaints if c.current_bureau})
        return data
