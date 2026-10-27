from datetime import datetime, timezone
import json
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import relationship
from .base import db

class CaseLink(db.Model):
    __tablename__ = "case_links"

    id = Column(Integer, primary_key=True, autoincrement=True)
    complaint_id_a = Column(Integer, ForeignKey("complaints.id", ondelete="CASCADE"), nullable=False, index=True)
    complaint_id_b = Column(Integer, ForeignKey("complaints.id", ondelete="CASCADE"), nullable=False, index=True)
    
    relationship_type = Column(String(50), default="potential_overlap", nullable=False) # "potential_overlap", "confirmed_related", "unrelated", "deferred"
    match_score = Column(Float, nullable=False, default=0.0) # 0.0 to 1.0
    match_method = Column(String(50), nullable=False) # "exact_identifier", "fuzzy_institution_name", "text_similarity", "hybrid"
    match_reason = Column(Text, nullable=False)
    evidence_json = Column(Text, nullable=True) # JSON with signals breakdown
    
    review_status = Column(String(30), default="pending", nullable=False) # "pending", "confirmed", "dismissed", "deferred"
    reviewed_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    review_remarks = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        UniqueConstraint("complaint_id_a", "complaint_id_b", name="uq_complaint_pair"),
        CheckConstraint("complaint_id_a < complaint_id_b", name="ck_ordered_complaint_pair"),
    )

    complaint_a = relationship("Complaint", foreign_keys=[complaint_id_a], back_populates="links_as_a")
    complaint_b = relationship("Complaint", foreign_keys=[complaint_id_b], back_populates="links_as_b")
    reviewed_by = relationship("User", foreign_keys=[reviewed_by_id])

    @property
    def evidence(self):
        if not self.evidence_json:
            return {}
        try:
            return json.loads(self.evidence_json)
        except Exception:
            return {}

    def set_evidence(self, data: dict):
        self.evidence_json = json.dumps(data)

    def to_dict(self, perspective_complaint_id=None):
        data = {
            "id": self.id,
            "complaint_id_a": self.complaint_id_a,
            "complaint_id_b": self.complaint_id_b,
            "relationship_type": self.relationship_type,
            "match_score": round(self.match_score, 2),
            "match_method": self.match_method,
            "match_reason": self.match_reason,
            "evidence": self.evidence,
            "review_status": self.review_status,
            "reviewed_by_name": self.reviewed_by.name if self.reviewed_by else None,
            "reviewed_by_id": self.reviewed_by_id,
            "reviewed_at": self.reviewed_at.isoformat() if self.reviewed_at else None,
            "review_remarks": self.review_remarks,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "case_a": {
                "id": self.complaint_a.id,
                "case_number": self.complaint_a.case_number,
                "subject": self.complaint_a.subject,
                "description": self.complaint_a.description,
                "category": self.complaint_a.category,
                "status": self.complaint_a.status,
                "priority": self.complaint_a.priority,
                "bureau_code": self.complaint_a.current_bureau.code if self.complaint_a and self.complaint_a.current_bureau else None,
                "institution_name": self.complaint_a.institution.name if self.complaint_a and self.complaint_a.institution else None,
                "institution_code": self.complaint_a.institution.institution_code if self.complaint_a and self.complaint_a.institution else None,
            } if self.complaint_a else None,
            "case_b": {
                "id": self.complaint_b.id,
                "case_number": self.complaint_b.case_number,
                "subject": self.complaint_b.subject,
                "description": self.complaint_b.description,
                "category": self.complaint_b.category,
                "status": self.complaint_b.status,
                "priority": self.complaint_b.priority,
                "bureau_code": self.complaint_b.current_bureau.code if self.complaint_b and self.complaint_b.current_bureau else None,
                "institution_name": self.complaint_b.institution.name if self.complaint_b and self.complaint_b.institution else None,
                "institution_code": self.complaint_b.institution.institution_code if self.complaint_b and self.complaint_b.institution else None,
            } if self.complaint_b else None,
        }
        if perspective_complaint_id:
            # Provide other_case helper for views focused on one complaint
            if perspective_complaint_id == self.complaint_id_a:
                data["other_case"] = data["case_b"]
            else:
                data["other_case"] = data["case_a"]
        return data
