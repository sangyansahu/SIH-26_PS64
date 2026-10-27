from datetime import datetime, timezone
import json
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .base import db

class ImportBatch(db.Model):
    __tablename__ = "import_batches"

    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String(255), nullable=False)
    total_rows = Column(Integer, default=0, nullable=False)
    success_rows = Column(Integer, default=0, nullable=False)
    failed_rows = Column(Integer, default=0, nullable=False)
    status = Column(String(30), default="completed", nullable=False) # "completed", "failed"
    errors_summary_json = Column(Text, nullable=True)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    created_by = relationship("User", foreign_keys=[created_by_id])

    @property
    def errors_summary(self):
        if not self.errors_summary_json:
            return []
        try:
            return json.loads(self.errors_summary_json)
        except Exception:
            return []

    def set_errors(self, errs):
        self.errors_summary_json = json.dumps(errs)

    def to_dict(self):
        return {
            "id": self.id,
            "filename": self.filename,
            "total_rows": self.total_rows,
            "success_rows": self.success_rows,
            "failed_rows": self.failed_rows,
            "status": self.status,
            "errors_summary": self.errors_summary,
            "created_by_name": self.created_by.name if self.created_by else "System",
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
