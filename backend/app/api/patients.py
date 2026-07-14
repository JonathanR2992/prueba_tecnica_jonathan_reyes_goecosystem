import re
from datetime import date, datetime
from typing import Any

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from app.extensions import db
from app.models import (
    Eps,
    Estado,
    Genero,
    Paciente,
    Prioridad,
    TipoDocumento,
)


patients_bp = Blueprint(
    "patients",
    __name__,
    url_prefix="/api/patients",
)


EMAIL_PATTERN = re.compile(
    r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
)

PHONE_PATTERN = re.compile(
    r"^[0-9+\-\s()]{7,20}$"
)

REQUIRED_FIELDS = (
    "tipo_documento",
    "documento",
    "nombre_completo",
    "fecha_nacimiento",
    "genero",
    "telefono",
    "eps_codigo",
    "prioridad",
    "estado",
)


def patient_relationship_options():
    """
    Retorna las relaciones que deben cargarse junto con un paciente.

    Esto evita consultas adicionales al serializar el paciente
    mediante to_dict().
    """
    return (
        joinedload(Paciente.tipo_documento_rel),
        joinedload(Paciente.genero_rel),
        joinedload(Paciente.eps_rel),
        joinedload(Paciente.prioridad_rel),
        joinedload(Paciente.estado_rel),
    )


def parse_date(value: Any) -> date | None:
    """Convierte una fecha YYYY-MM-DD en un objeto date."""
    if not isinstance(value, str):
        return None

    try:
        return datetime.strptime(
            value.strip(),
            "%Y-%m-%d",
        ).date()
    except ValueError:
        return None


def normalize_optional_text(value: Any) -> str | None:
    """Normaliza un texto opcional y convierte vacíos en None."""
    if value is None:
        return None

    normalized_value = str(value).strip()

    return normalized_value or None


def normalize_required_text(value: Any) -> str:
    """Normaliza un campo textual obligatorio."""
    if value is None:
        return ""

    return str(value).strip()


def normalize_patient_payload(
    payload: dict[str, Any],
) -> dict[str, Any]:
    """Normaliza los datos recibidos desde la solicitud."""
    return {
        "tipo_documento": normalize_required_text(
            payload.get("tipo_documento")
        ),
        "documento": normalize_required_text(
            payload.get("documento")
        ),
        "nombre_completo": normalize_required_text(
            payload.get("nombre_completo")
        ),
        "fecha_nacimiento": payload.get(
            "fecha_nacimiento"
        ),
        "genero": normalize_required_text(
            payload.get("genero")
        ),
        "telefono": normalize_required_text(
            payload.get("telefono")
        ),
        "correo": normalize_optional_text(
            payload.get("correo")
        ),
        "eps_codigo": normalize_required_text(
            payload.get("eps_codigo")
        ),
        "ciudad": normalize_optional_text(
            payload.get("ciudad")
        ),
        "prioridad": normalize_required_text(
            payload.get("prioridad")
        ),
        "estado": normalize_required_text(
            payload.get("estado")
        ),
    }


def catalog_value_exists(
    model,
    field,
    value: str,
) -> bool:
    """Verifica que un valor exista y esté activo en un catálogo."""
    statement = (
        db.select(model)
        .where(
            field == value,
            model.activo.is_(True),
        )
        .limit(1)
    )

    return (
        db.session.execute(statement)
        .scalar_one_or_none()
        is not None
    )


def document_already_exists(
    document: str,
    excluded_patient_id: int | None = None,
) -> bool:
    """
    Verifica si un documento ya pertenece a otro paciente.

    En actualizaciones se excluye el paciente que está siendo editado.
    """
    statement = db.select(Paciente.paciente_id).where(
        Paciente.documento == document
    )

    if excluded_patient_id is not None:
        statement = statement.where(
            Paciente.paciente_id != excluded_patient_id
        )

    statement = statement.limit(1)

    return (
        db.session.execute(statement).scalar_one_or_none()
        is not None
    )


def validate_catalogs(
    fields: dict[str, Any],
    errors: dict[str, str],
) -> None:
    """Valida los valores asociados con tablas catálogo."""
    catalog_validations = (
        (
            "tipo_documento",
            TipoDocumento,
            TipoDocumento.codigo,
            "El tipo de documento no existe o está inactivo",
        ),
        (
            "genero",
            Genero,
            Genero.nombre,
            "El género no existe o está inactivo",
        ),
        (
            "eps_codigo",
            Eps,
            Eps.eps_codigo,
            "La EPS no existe o está inactiva",
        ),
        (
            "prioridad",
            Prioridad,
            Prioridad.nombre,
            "La prioridad no existe o está inactiva",
        ),
        (
            "estado",
            Estado,
            Estado.nombre,
            "El estado no existe o está inactivo",
        ),
    )

    for field_name, model, model_field, error_message in catalog_validations:
        value = fields.get(field_name)

        if (
            value
            and not catalog_value_exists(
                model,
                model_field,
                value,
            )
        ):
            errors[field_name] = error_message


def validate_patient_fields(
    fields: dict[str, Any],
    excluded_patient_id: int | None = None,
) -> tuple[dict[str, str], date | None]:
    """
    Valida todos los campos de un paciente.

    Retorna:
    - Diccionario de errores.
    - Fecha de nacimiento convertida.
    """
    errors: dict[str, str] = {}

    for field_name in REQUIRED_FIELDS:
        if not fields.get(field_name):
            errors[field_name] = "Este campo es obligatorio"

    birth_date = parse_date(
        fields.get("fecha_nacimiento")
    )

    if fields.get("fecha_nacimiento"):
        if birth_date is None:
            errors["fecha_nacimiento"] = (
                "La fecha debe tener formato YYYY-MM-DD"
            )
        elif birth_date > date.today():
            errors["fecha_nacimiento"] = (
                "La fecha de nacimiento no puede ser futura"
            )

    full_name = fields.get("nombre_completo", "")

    if full_name and not 3 <= len(full_name) <= 150:
        errors["nombre_completo"] = (
            "El nombre debe tener entre 3 y 150 caracteres"
        )

    document = fields.get("documento", "")

    if document:
        if not 3 <= len(document) <= 20:
            errors["documento"] = (
                "El documento debe tener entre 3 y 20 caracteres"
            )
        elif document_already_exists(
            document,
            excluded_patient_id=excluded_patient_id,
        ):
            errors["documento"] = (
                "Ya existe otro paciente con este documento"
                if excluded_patient_id is not None
                else "Ya existe un paciente con este documento"
            )

    phone = fields.get("telefono", "")

    if phone and not PHONE_PATTERN.fullmatch(phone):
        errors["telefono"] = (
            "El teléfono debe tener entre 7 y 20 caracteres "
            "y contener únicamente números o símbolos "
            "telefónicos válidos"
        )

    email = fields.get("correo")

    if email:
        if len(email) > 150:
            errors["correo"] = (
                "El correo no puede superar 150 caracteres"
            )
        elif not EMAIL_PATTERN.fullmatch(email):
            errors["correo"] = (
                "El formato del correo no es válido"
            )

    city = fields.get("ciudad")

    if city and len(city) > 80:
        errors["ciudad"] = (
            "La ciudad no puede superar 80 caracteres"
        )

    validate_catalogs(
        fields,
        errors,
    )

    return errors, birth_date


def validation_error_response(
    errors: dict[str, str],
):
    """Construye una respuesta uniforme para errores de validación."""
    return jsonify(
        {
            "error": "validation_error",
            "message": "Los datos enviados no son válidos",
            "details": errors,
        }
    ), 400


def get_patient_with_relationships(
    patient_id: int,
) -> Paciente | None:
    """Consulta un paciente cargando sus relaciones."""
    statement = (
        db.select(Paciente)
        .options(
            *patient_relationship_options()
        )
        .where(
            Paciente.paciente_id == patient_id
        )
    )

    return db.session.execute(
        statement
    ).scalar_one_or_none()


def assign_patient_fields(
    patient: Paciente,
    fields: dict[str, Any],
    birth_date: date,
) -> None:
    """Asigna al modelo los campos normalizados y validados."""
    patient.tipo_documento = fields["tipo_documento"]
    patient.documento = fields["documento"]
    patient.nombre_completo = fields["nombre_completo"]
    patient.fecha_nacimiento = birth_date
    patient.genero = fields["genero"]
    patient.telefono = fields["telefono"]
    patient.correo = fields["correo"]
    patient.eps_codigo = fields["eps_codigo"]
    patient.ciudad = fields["ciudad"]
    patient.prioridad = fields["prioridad"]
    patient.estado = fields["estado"]
    patient.fecha_actualizacion = datetime.now()


def integrity_error_response(action: str):
    """Construye la respuesta para errores de integridad."""
    return jsonify(
        {
            "error": "integrity_error",
            "message": (
                f"No fue posible {action} el paciente "
                "por una restricción de integridad"
            ),
        }
    ), 409


@patients_bp.get("")
@jwt_required()
def get_patients():
    """
    Retorna pacientes con búsqueda, filtros y paginación.

    Parámetros:
    - page: página actual.
    - per_page: registros por página.
    - search: nombre o documento.
    - status: estado de atención.
    - priority: prioridad.
    - eps_codigo: código de EPS.
    """
    page = request.args.get(
        "page",
        default=1,
        type=int,
    )

    per_page = request.args.get(
        "per_page",
        default=10,
        type=int,
    )

    search = request.args.get(
        "search",
        default="",
        type=str,
    ).strip()

    status = request.args.get(
        "status",
        default="",
        type=str,
    ).strip()

    priority = request.args.get(
        "priority",
        default="",
        type=str,
    ).strip()

    eps_codigo = request.args.get(
        "eps_codigo",
        default="",
        type=str,
    ).strip()

    if page < 1:
        return jsonify(
            {
                "error": "validation_error",
                "message": "La página debe ser mayor o igual a 1",
            }
        ), 400

    if not 1 <= per_page <= 100:
        return jsonify(
            {
                "error": "validation_error",
                "message": (
                    "La cantidad de registros por página "
                    "debe estar entre 1 y 100"
                ),
            }
        ), 400

    statement = (
        db.select(Paciente)
        .join(
            Prioridad,
            Paciente.prioridad == Prioridad.nombre,
        )
        .options(
            *patient_relationship_options()
        )
    )

    if search:
        search_pattern = f"%{search}%"

        statement = statement.where(
            or_(
                Paciente.nombre_completo.ilike(
                    search_pattern
                ),
                Paciente.documento.ilike(
                    search_pattern
                ),
            )
        )

    if status:
        statement = statement.where(
            Paciente.estado == status
        )

    if priority:
        statement = statement.where(
            Paciente.prioridad == priority
        )

    if eps_codigo:
        statement = statement.where(
            Paciente.eps_codigo == eps_codigo
        )

    statement = statement.order_by(
        Prioridad.nivel.asc(),
        Paciente.fecha_creacion.asc(),
        Paciente.paciente_id.asc(),
    )

    pagination = db.paginate(
        statement,
        page=page,
        per_page=per_page,
        error_out=False,
    )

    return jsonify(
        {
            "items": [
                patient.to_dict()
                for patient in pagination.items
            ],
            "pagination": {
                "page": pagination.page,
                "per_page": pagination.per_page,
                "total": pagination.total,
                "pages": pagination.pages,
                "has_next": pagination.has_next,
                "has_prev": pagination.has_prev,
                "next_page": (
                    pagination.next_num
                    if pagination.has_next
                    else None
                ),
                "previous_page": (
                    pagination.prev_num
                    if pagination.has_prev
                    else None
                ),
            },
            "filters": {
                "search": search or None,
                "status": status or None,
                "priority": priority or None,
                "eps_codigo": eps_codigo or None,
            },
        }
    ), 200


@patients_bp.get("/<int:patient_id>")
@jwt_required()
def get_patient_by_id(patient_id: int):
    """Retorna un paciente específico por su identificador."""
    patient = get_patient_with_relationships(
        patient_id
    )

    if patient is None:
        return jsonify(
            {
                "error": "patient_not_found",
                "message": (
                    f"No existe un paciente con el id {patient_id}"
                ),
            }
        ), 404

    return jsonify(
        {
            "patient": patient.to_dict(),
        }
    ), 200


@patients_bp.post("")
@jwt_required()
def create_patient():
    """Crea un nuevo paciente."""
    payload = request.get_json(silent=True)

    if not isinstance(payload, dict):
        return jsonify(
            {
                "error": "invalid_json",
                "message": (
                    "El cuerpo debe contener un JSON válido"
                ),
            }
        ), 400

    fields = normalize_patient_payload(
        payload
    )

    errors, birth_date = validate_patient_fields(
        fields
    )

    if errors:
        return validation_error_response(
            errors
        )

    now = datetime.now()

    patient = Paciente(
        fecha_creacion=now,
        fecha_actualizacion=now,
    )

    assign_patient_fields(
        patient,
        fields,
        birth_date,
    )

    try:
        db.session.add(patient)
        db.session.commit()

    except IntegrityError:
        db.session.rollback()
        return integrity_error_response(
            "crear"
        )

    created_patient = get_patient_with_relationships(
        patient.paciente_id
    )

    return jsonify(
        {
            "message": "Paciente creado correctamente",
            "patient": created_patient.to_dict(),
        }
    ), 201


@patients_bp.put("/<int:patient_id>")
@jwt_required()
def update_patient(patient_id: int):
    """Actualiza completamente un paciente existente."""
    patient = db.session.get(
        Paciente,
        patient_id,
    )

    if patient is None:
        return jsonify(
            {
                "error": "patient_not_found",
                "message": (
                    f"No existe un paciente con el id {patient_id}"
                ),
            }
        ), 404

    payload = request.get_json(silent=True)

    if not isinstance(payload, dict):
        return jsonify(
            {
                "error": "invalid_json",
                "message": (
                    "El cuerpo debe contener un JSON válido"
                ),
            }
        ), 400

    fields = normalize_patient_payload(
        payload
    )

    errors, birth_date = validate_patient_fields(
        fields,
        excluded_patient_id=patient_id,
    )

    if errors:
        return validation_error_response(
            errors
        )

    assign_patient_fields(
        patient,
        fields,
        birth_date,
    )

    try:
        db.session.commit()

    except IntegrityError:
        db.session.rollback()
        return integrity_error_response(
            "actualizar"
        )

    updated_patient = get_patient_with_relationships(
        patient_id
    )

    return jsonify(
        {
            "message": "Paciente actualizado correctamente",
            "patient": updated_patient.to_dict(),
        }
    ), 200


@patients_bp.delete("/<int:patient_id>")
@jwt_required()
def delete_patient(patient_id: int):
    """Elimina físicamente un paciente."""
    patient = db.session.get(
        Paciente,
        patient_id,
    )

    if patient is None:
        return jsonify(
            {
                "error": "patient_not_found",
                "message": (
                    f"No existe un paciente con el id {patient_id}"
                ),
            }
        ), 404

    patient_data = {
        "paciente_id": patient.paciente_id,
        "documento": patient.documento,
        "nombre_completo": patient.nombre_completo,
    }

    try:
        db.session.delete(patient)
        db.session.commit()

    except IntegrityError:
        db.session.rollback()
        return integrity_error_response(
            "eliminar"
        )

    return jsonify(
        {
            "message": "Paciente eliminado correctamente",
            "patient": patient_data,
        }
    ), 200