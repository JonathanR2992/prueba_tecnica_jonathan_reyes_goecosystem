from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import func, select

from app.extensions import db
from app.models import Paciente


dashboard_bp = Blueprint(
    "dashboard",
    __name__,
    url_prefix="/api/dashboard",
)


@dashboard_bp.get("")
@jwt_required()
def get_dashboard():
    """
    Retorna los indicadores operativos principales
    del módulo de seguimiento de pacientes.
    """

    total_pacientes = db.session.scalar(
        select(func.count(Paciente.paciente_id))
    )

    pacientes_pendientes = db.session.scalar(
        select(func.count(Paciente.paciente_id))
        .where(Paciente.estado == "Pendiente")
    )

    pacientes_en_atencion = db.session.scalar(
        select(func.count(Paciente.paciente_id))
        .where(Paciente.estado == "En atención")
    )

    pacientes_atendidos = db.session.scalar(
        select(func.count(Paciente.paciente_id))
        .where(Paciente.estado == "Atendido")
    )

    pacientes_prioridad_alta = db.session.scalar(
        select(func.count(Paciente.paciente_id))
        .where(Paciente.prioridad == "Alta")
    )

    pendientes_prioridad_alta = db.session.scalar(
        select(func.count(Paciente.paciente_id))
        .where(
            Paciente.estado == "Pendiente",
            Paciente.prioridad == "Alta",
        )
    )

    return jsonify(
        {
            "total_pacientes": total_pacientes or 0,
            "pacientes_pendientes": pacientes_pendientes or 0,
            "pacientes_en_atencion": pacientes_en_atencion or 0,
            "pacientes_atendidos": pacientes_atendidos or 0,
            "pacientes_prioridad_alta": (
                pacientes_prioridad_alta or 0
            ),
            "pendientes_prioridad_alta": (
                pendientes_prioridad_alta or 0
            ),
        }
    ), 200