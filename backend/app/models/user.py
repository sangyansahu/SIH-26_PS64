from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .base import db

class User(db.Model):
    __tablename__ = "users"

    ROLE_SYSTEM_ADMIN = "SYSTEM_ADMIN"
    ROLE_INDUSTRY = "INDUSTRY"
    ROLE_USER = "USER"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(120), nullable=False)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="INDUSTRY")  # "SYSTEM_ADMIN", "INDUSTRY", "USER"
    bureau_id = Column(Integer, ForeignKey("bureaus.id"), nullable=True)
    designation = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    last_login_at = Column(DateTime, nullable=True)

    @property
    def is_system_admin(self) -> bool:
        return (self.role or "").strip().upper() in ("SYSTEM_ADMIN", "ADMIN")

    @property
    def is_industry(self) -> bool:
        return (self.role or "").strip().upper() in ("INDUSTRY", "OFFICER", "SENIOR_AUTHORITY")

    @property
    def is_user(self) -> bool:
        return (self.role or "").strip().upper() in ("USER", "CITIZEN")


    bureau = relationship("Bureau", back_populates="users")
    assigned_complaints = relationship("Complaint", foreign_keys="Complaint.assigned_user_id", back_populates="assigned_officer")
    notifications = relationship("Notification", back_populates="user")

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    @property
    def canonical_role(self) -> str:
        r = (self.role or "").strip().upper()
        if r in ("SYSTEM_ADMIN", "ADMIN"):
            return self.ROLE_SYSTEM_ADMIN
        if r in ("USER", "CITIZEN"):
            return self.ROLE_USER
        return self.ROLE_INDUSTRY

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.canonical_role,
            "bureau_id": self.bureau_id,
            "bureau_code": self.bureau.code if self.bureau else None,
            "bureau_name": self.bureau.name if self.bureau else None,
            "designation": self.designation,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login_at": self.last_login_at.isoformat() if self.last_login_at else None,
        }
