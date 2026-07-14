from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

from app.extensions import db
from app.models import (
    Eps,
    Estado,
    Genero,
    Prioridad,
    TipoDocumento,
)


catalogs_bp = Blueprint(
    "catalogs",
    __name__,
    url_prefix="/api/catalogs",
)


@catalogs_bp.get("")
@jwt_required()
def get_catalogs():
    """
    Retorna los catálogos activos necesarios para los
    formularios de creación y edición de pacientes.
    """

    tipos_documento = db.session.execute(
        db.select(TipoDocumento)
        .where(TipoDocumento.activo.is_(True))
        .order_by(TipoDocumento.nombre.asc())
    ).scalars().all()

    generos = db.session.execute(
        db.select(Genero)
        .where(Genero.activo.is_(True))
        .order_by(Genero.nombre.asc())
    ).scalars().all()

    eps_list = db.session.execute(
        db.select(Eps)
        .where(Eps.activo.is_(True))
        .order_by(Eps.eps_nombre.asc())
    ).scalars().all()

    prioridades = db.session.execute(
        db.select(Prioridad)
        .where(Prioridad.activo.is_(True))
        .order_by(Prioridad.nivel.asc())
    ).scalars().all()

    estados = db.session.execute(
        db.select(Estado)
        .where(Estado.activo.is_(True))
        .order_by(Estado.nombre.asc())
    ).scalars().all()

    return jsonify(
        {
            "tipos_documento": [
                tipo.to_dict()
                for tipo in tipos_documento
            ],
            "generos": [
                genero.to_dict()
                for genero in generos
            ],
            "eps": [
                eps.to_dict()
                for eps in eps_list
            ],
            "prioridades": [
                prioridad.to_dict()
                for prioridad in prioridades
            ],
            "estados": [
                estado.to_dict()
                for estado in estados
            ],
        }
    ), 200