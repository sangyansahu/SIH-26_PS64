from flask import Blueprint, request, jsonify
from ..services.auth_service import (
    jwt_required,
    roles_required,
    get_current_user,
    ROLE_SYSTEM_ADMIN,
    ROLE_INDUSTRY,
    ROLE_USER,
)
from ..services.notification_service import (
    get_user_notifications,
    mark_notification_as_read,
    mark_all_notifications_as_read,
    check_and_create_deadline_alerts,
)

notifications_bp = Blueprint("notifications", __name__, url_prefix="/api/v1/notifications")

@notifications_bp.route("", methods=["GET"])
@jwt_required
def list_notifications():
    unread_only = request.args.get("unread_only", "").lower() == "true"
    user = get_current_user()
    data = get_user_notifications(user, unread_only=unread_only)
    return jsonify(data)

@notifications_bp.route("/<int:notif_id>/read", methods=["PATCH"])
@jwt_required
def mark_read(notif_id: int):
    user = get_current_user()
    notif, err = mark_notification_as_read(notif_id, user)
    if err:
        return jsonify({"error": err}), 404
    return jsonify({"message": "Marked as read", "notification": notif.to_dict()})

@notifications_bp.route("/read-all", methods=["POST"])
@jwt_required
def mark_all_read():
    user = get_current_user()
    mark_all_notifications_as_read(user)
    return jsonify({"message": "All notifications marked as read"})

@notifications_bp.route("/check-deadlines", methods=["POST"])
@jwt_required
@roles_required(ROLE_SYSTEM_ADMIN, ROLE_INDUSTRY)
def trigger_deadline_check():
    created = check_and_create_deadline_alerts()
    return jsonify({"message": f"Deadline scan complete. Created {created} alerts."})
