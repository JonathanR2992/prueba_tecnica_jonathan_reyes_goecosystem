from flask import Flask, jsonify
from flask_cors import CORS
from sqlalchemy import text

from app.config import Config
from app.extensions import db, jwt

from app.api import register_blueprints


def create_app() -> Flask:
    """Crea y configura la aplicación Flask."""

    app = Flask(__name__)
    app.config.from_object(Config)
    
    app.json.ensure_ascii = False

    initialize_extensions(app)
    
    def import_models() -> None:
        """Registra los modelos SQLAlchemy."""
        from app import models  # noqa: F401
    
    import_models()
    register_blueprints(app)
    register_routes(app)
    register_error_handlers(app)
    register_jwt_handlers()

    return app


def initialize_extensions(app: Flask) -> None:
    """Inicializa las extensiones utilizadas por la aplicación."""

    db.init_app(app)
    jwt.init_app(app)

    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": [
                    app.config["FRONTEND_URL"],
                ],
            }
        },
    )


def register_routes(app: Flask) -> None:
    """Registra las rutas iniciales de la aplicación."""

    @app.get("/")
    def index():
        return jsonify(
            {
                "application": "Sistema de gestión de pacientes",
                "status": "running",
            }
        ), 200

    @app.get("/api/health")
    def health():
        try:
            db.session.execute(text("SELECT 1"))

            return jsonify(
                {
                    "status": "ok",
                    "database": "connected",
                    "message": (
                        "La API y MariaDB están disponibles"
                    ),
                }
            ), 200

        except Exception as error:
            app.logger.exception(
                "No fue posible conectar con MariaDB"
            )

            return jsonify(
                {
                    "status": "error",
                    "database": "disconnected",
                    "message": (
                        "No fue posible conectar con MariaDB"
                    ),
                    "detail": str(error),
                }
            ), 500
    
    @app.get("/api/test/models")
    def test_models():
        from app.models import Eps, Paciente, Usuario

        total_pacientes = db.session.query(
            Paciente
        ).count()

        total_usuarios = db.session.query(
            Usuario
        ).count()

        total_eps = db.session.query(
            Eps
        ).count()

        primer_paciente = (
            db.session.query(Paciente)
            .order_by(Paciente.paciente_id.asc())
            .first()
        )

        return jsonify(
            {
                "total_pacientes": total_pacientes,
                "total_usuarios": total_usuarios,
                "total_eps": total_eps,
                "primer_paciente": (
                    primer_paciente.to_dict()
                    if primer_paciente
                    else None
                ),
            }
        ), 200


def register_jwt_handlers() -> None:
    @jwt.unauthorized_loader
    def missing_token(reason: str):
        return jsonify(
            {
                "error": "authorization_required",
                "message": "Se requiere un token de acceso",
            }
        ), 401

    @jwt.invalid_token_loader
    def invalid_token(reason: str):
        return jsonify(
            {
                "error": "invalid_token",
                "message": "El token enviado no es válido",
            }
        ), 422

    @jwt.expired_token_loader
    def expired_token(jwt_header, jwt_payload):
        return jsonify(
            {
                "error": "expired_token",
                "message": "El token de acceso ha expirado",
            }
        ), 401

    @jwt.revoked_token_loader
    def revoked_token(jwt_header, jwt_payload):
        return jsonify(
            {
                "error": "revoked_token",
                "message": "El token fue revocado",
            }
        ), 401

def register_error_handlers(app: Flask) -> None:
    """Registra manejadores generales de errores HTTP."""

    @app.errorhandler(404)
    def not_found(error):
        return jsonify(
            {
                "error": "not_found",
                "message": "El recurso solicitado no existe",
            }
        ), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify(
            {
                "error": "method_not_allowed",
                "message": (
                    "El método HTTP no está permitido "
                    "para este recurso"
                ),
            }
        ), 405

    @app.errorhandler(500)
    def internal_server_error(error):
        db.session.rollback()

        return jsonify(
            {
                "error": "internal_server_error",
                "message": "Ocurrió un error interno",
            }
        ), 500