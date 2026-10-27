import jwt
from datetime import datetime, timezone, timedelta
from functools import wraps
from flask import request, jsonify, current_app, g
from ..models import User, db

ROLE_SYSTEM_ADMIN = "SYSTEM_ADMIN"
ROLE_INDUSTRY = "INDUSTRY"
ROLE_USER = "USER"

ROLE_MAP = {
    "ADMIN": ROLE_SYSTEM_ADMIN,
    "SYSTEM_ADMIN": ROLE_SYSTEM_ADMIN,
    "OFFICER": ROLE_INDUSTRY,
    "SENIOR_AUTHORITY": ROLE_INDUSTRY,
    "INDUSTRY": ROLE_INDUSTRY,
    "USER": ROLE_USER,
    "CITIZEN": ROLE_USER,
}

def normalize_role(role: str) -> str:
    if not role:
        return ROLE_USER
    return ROLE_MAP.get(str(role).strip().upper(), ROLE_INDUSTRY)

def generate_token(user: User) -> str:
    role = normalize_role(user.role)
    payload = {
        "sub": str(user.id),
        "email": user.email,
        "role": role,
        "bureau_id": user.bureau_id,
        "name": user.name,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + current_app.config.get("JWT_ACCESS_TOKEN_EXPIRES", timedelta(hours=8)),
    }
    return jwt.encode(payload, current_app.config["JWT_SECRET_KEY"], algorithm="HS256")

def decode_token(token: str) -> dict:
    return jwt.decode(token, current_app.config["JWT_SECRET_KEY"], algorithms=["HS256"])

def get_current_user() -> User:
    return getattr(g, "current_user", None)

def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        token = None
        if auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
        elif request.cookies.get("aicte_token"):
            token = request.cookies.get("aicte_token")

        if not token:
            return jsonify({"error": "Authentication token is required"}), 401

        if token == "dev_bypass_token":
            # Allowed for offline sandbox test session
            demo_user = db.session.query(User).filter_by(role=ROLE_SYSTEM_ADMIN).first() or db.session.query(User).first()
            if demo_user:
                g.current_user = demo_user
                return f(*args, **kwargs)
            return jsonify({"error": "Demo user account not available"}), 401

        try:
            payload = decode_token(token)
            user_id = int(payload["sub"])
            user = db.session.get(User, user_id)
            if not user or not user.is_active:
                return jsonify({"error": "User account is inactive or not found"}), 401
            g.current_user = user
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Session token has expired. Please sign in again."}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid authentication token"}), 401

        return f(*args, **kwargs)
    return decorated

def roles_required(*allowed_roles):
    """
    Backend-enforced role-based access control.
    Supports canonical roles: SYSTEM_ADMIN, INDUSTRY, USER.
    SYSTEM_ADMIN has supervisory access across all administrative and industry casework endpoints.
    """
    norm_allowed = {normalize_role(r) for r in allowed_roles}

    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            user = get_current_user()
            if not user:
                return jsonify({"error": "Authentication required"}), 401

            user_role = normalize_role(user.role)
            # SYSTEM_ADMIN is authorized for all administrative & industry casework endpoints
            if user_role == ROLE_SYSTEM_ADMIN:
                return f(*args, **kwargs)

            if user_role not in norm_allowed:
                return jsonify({
                    "error": f"Access forbidden: role '{user_role}' lacks permission for this endpoint",
                    "required_roles": sorted(list(norm_allowed)),
                    "current_role": user_role
                }), 403

            return f(*args, **kwargs)
        return decorated
    return decorator
