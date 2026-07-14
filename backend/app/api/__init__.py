"""Módulos de rutas de la API REST."""

from flask import Flask

from app.api.auth import auth_bp
from app.api.catalogs import catalogs_bp
from app.api.dashboard import dashboard_bp
from app.api.patients import patients_bp


def register_blueprints(app: Flask) -> None:
    """Registra los Blueprints de la API REST."""

    app.register_blueprint(auth_bp)
    app.register_blueprint(catalogs_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(patients_bp)