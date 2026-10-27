from flask import Blueprint, request, jsonify, Response
from ..services.auth_service import jwt_required, roles_required, ROLE_SYSTEM_ADMIN, ROLE_INDUSTRY
from ..services.report_service import (
    get_dashboard_kpis,
    get_analytics_breakdown,
    generate_cases_csv,
    get_disposal_rates_report,
    get_ageing_report,
    get_recurring_institutions_report,
    generate_report_csv,
)

reports_bp = Blueprint("reports", __name__, url_prefix="/api/v1/reports")

@reports_bp.route("/kpis", methods=["GET"])
@jwt_required
@roles_required(ROLE_SYSTEM_ADMIN, ROLE_INDUSTRY)
def get_kpis():
    bureau_id = request.args.get("bureau_id", type=int)
    data = get_dashboard_kpis(bureau_id=bureau_id)
    return jsonify(data)

@reports_bp.route("/analytics", methods=["GET"])
@jwt_required
@roles_required(ROLE_SYSTEM_ADMIN, ROLE_INDUSTRY)
def get_analytics():
    bureau_id = request.args.get("bureau_id", type=int)
    state = request.args.get("state")
    data = get_analytics_breakdown(bureau_id=bureau_id, state=state)
    return jsonify(data)

@reports_bp.route("/disposal-rates", methods=["GET"])
@jwt_required
@roles_required(ROLE_SYSTEM_ADMIN, ROLE_INDUSTRY)
def get_disposal_rates():
    period = request.args.get("period", "monthly")
    data = get_disposal_rates_report(period=period)
    return jsonify({"report": data, "period": period})

@reports_bp.route("/ageing", methods=["GET"])
@jwt_required
@roles_required(ROLE_SYSTEM_ADMIN, ROLE_INDUSTRY)
def get_ageing():
    data = get_ageing_report()
    return jsonify({"ageing_bands": data})

@reports_bp.route("/recurring", methods=["GET"])
@jwt_required
@roles_required(ROLE_SYSTEM_ADMIN, ROLE_INDUSTRY)
def get_recurring():
    data = get_recurring_institutions_report()
    return jsonify({"recurring_institutions": data})

@reports_bp.route("/export-csv", methods=["GET"])
@jwt_required
@roles_required(ROLE_SYSTEM_ADMIN, ROLE_INDUSTRY)
def export_csv():
    report_type = request.args.get("type", "cases")
    bureau_id = request.args.get("bureau_id", type=int)
    status = request.args.get("status")
    priority = request.args.get("priority")

    if report_type in ("disposal", "ageing", "recurring"):
        csv_data = generate_report_csv(report_type)
        filename = f"aicte_{report_type}_report.csv"
    else:
        csv_data = generate_cases_csv(bureau_id=bureau_id, status=status, priority=priority)
        filename = "aicte_complaints_export.csv"

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-disposition": f"attachment; filename={filename}"}
    )

