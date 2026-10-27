from flask import Flask, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from .models.base import db
from .api import register_blueprints
from config import Config

migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    
    CORS(
        app,
        resources={r"/api/*": {"origins": app.config.get("CORS_ORIGINS", "*")}},
        supports_credentials=True,
        expose_headers=["Content-Disposition"]
    )

    # Register all API endpoints
    register_blueprints(app)

    @app.route("/api/health", methods=["GET"])
    def health_check():
        return jsonify({
            "status": "healthy",
            "service": "AICTE Integrated Complaint Monitoring & Coordination Portal",
            "database": "PostgreSQL",
            "version": "1.0.0-SIH2026"
        })

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.session.remove()

    # Global Error Handlers
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"error": "Bad request", "details": str(e)}), 400

    @app.errorhandler(401)
    def unauthorized(e):
        return jsonify({"error": "Unauthorized"}), 401

    @app.errorhandler(403)
    def forbidden(e):
        return jsonify({"error": "Forbidden"}), 403

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": "Internal server error"}), 500

    return app
