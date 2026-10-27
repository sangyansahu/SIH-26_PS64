from flask import Blueprint
from .auth import auth_bp
from .institutions import institutions_bp
from .complaints import complaints_bp
from .bureaus import bureaus_bp
from .overlaps import overlaps_bp
from .reports import reports_bp
from .notifications import notifications_bp
from .imports import imports_bp
from .admin import admin_bp
from .public import public_bp

def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(institutions_bp)
    app.register_blueprint(complaints_bp)
    app.register_blueprint(bureaus_bp)
    app.register_blueprint(overlaps_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(imports_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(public_bp)
