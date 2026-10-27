from datetime import datetime, timezone, timedelta
from sqlalchemy import or_, and_, desc
from ..models import db, Notification, Complaint, User

def get_user_notifications(current_user: User, unread_only=False, limit=50):
    query = db.session.query(Notification).filter(
        or_(
            Notification.user_id == current_user.id,
            and_(Notification.bureau_id == current_user.bureau_id, Notification.user_id.is_(None)),
            and_(Notification.role == current_user.role, Notification.user_id.is_(None)),
            and_(Notification.user_id.is_(None), Notification.bureau_id.is_(None), Notification.role.is_(None))
        )
    )

    if unread_only:
        query = query.filter(Notification.read_at.is_(None))

    query = query.order_by(desc(Notification.created_at)).limit(limit)
    items = query.all()
    unread_count = db.session.query(Notification).filter(
        or_(
            Notification.user_id == current_user.id,
            and_(Notification.bureau_id == current_user.bureau_id, Notification.user_id.is_(None)),
            and_(Notification.role == current_user.role, Notification.user_id.is_(None)),
            and_(Notification.user_id.is_(None), Notification.bureau_id.is_(None), Notification.role.is_(None))
        ),
        Notification.read_at.is_(None)
    ).count()

    return {
        "notifications": [item.to_dict() for item in items],
        "unread_count": unread_count
    }

def mark_notification_as_read(notification_id: int, current_user: User):
    notif = db.session.get(Notification, notification_id)
    if not notif:
        return None, "Notification not found"

    notif.read_at = datetime.now(timezone.utc)
    db.session.commit()
    return notif, None

def mark_all_notifications_as_read(current_user: User):
    now = datetime.now(timezone.utc)
    db.session.query(Notification).filter(
        or_(
            Notification.user_id == current_user.id,
            and_(Notification.bureau_id == current_user.bureau_id, Notification.user_id.is_(None)),
            and_(Notification.role == current_user.role, Notification.user_id.is_(None)),
        ),
        Notification.read_at.is_(None)
    ).update({"read_at": now}, synchronize_session=False)
    db.session.commit()
    return True

def check_and_create_deadline_alerts():
    """
    Check for cases approaching due dates (within 48 hours) or overdue cases,
    and create alert notifications.
    """
    now = datetime.now(timezone.utc)
    near_threshold = now + timedelta(hours=48)

    # Overdue open cases
    overdue_cases = db.session.query(Complaint).filter(
        Complaint.status.notin_(["Disposed", "Closed"]),
        Complaint.due_at.isnot(None),
        Complaint.due_at < now
    ).all()

    created_alerts = 0
    for case in overdue_cases:
        # Check if overdue alert already sent today
        existing = db.session.query(Notification).filter(
            Notification.related_complaint_id == case.id,
            Notification.notification_type == "case_overdue"
        ).first()

        if not existing:
            notif = Notification(
                bureau_id=case.current_bureau_id,
                user_id=case.assigned_user_id,
                notification_type="case_overdue",
                title=f"URGENT: Case Overdue - {case.case_number}",
                message=f"Complaint {case.case_number} ({case.subject[:60]}...) for {case.institution.name} has passed its due date and requires immediate regulatory action.",
                related_complaint_id=case.id,
            )
            db.session.add(notif)
            created_alerts += 1

    db.session.commit()
    return created_alerts
