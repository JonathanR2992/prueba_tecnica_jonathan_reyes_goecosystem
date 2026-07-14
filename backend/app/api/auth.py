from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    get_jwt,
    get_jwt_identity,
    jwt_required,
)

from app.extensions import db
from app.models import Usuario


auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/api/auth",
)


@auth_bp.post("/login")
def login():
    """
    Valida las credenciales y genera un token JWT.

    En esta prueba técnica la contraseña se compara en texto plano
    contra el campo password_demo.
    """
    payload = request.get_json(silent=True) or {}

    usuario_ingresado = str(
        payload.get("usuario", "")
    ).strip()

    password_ingresado = str(
        payload.get("password", "")
    )

    errores = {}

    if not usuario_ingresado:
        errores["usuario"] = "El usuario es obligatorio"

    if not password_ingresado:
        errores["password"] = "La contraseña es obligatoria"

    if errores:
        return jsonify(
            {
                "error": "validation_error",
                "message": "Los datos enviados no son válidos",
                "details": errores,
            }
        ), 400

    usuario = db.session.execute(
        db.select(Usuario).where(
            Usuario.usuario == usuario_ingresado
        )
    ).scalar_one_or_none()

    credenciales_validas = (
        usuario is not None
        and usuario.activo is True
        and usuario.password_demo == password_ingresado
    )

    if not credenciales_validas:
        return jsonify(
            {
                "error": "invalid_credentials",
                "message": "Usuario o contraseña incorrectos",
            }
        ), 401

    claims = {
        "usuario": usuario.usuario,
        "nombre": usuario.nombre,
        "rol": usuario.rol,
    }

    access_token = create_access_token(
        identity=str(usuario.usuario_id),
        additional_claims=claims,
    )

    return jsonify(
        {
            "message": "Inicio de sesión exitoso",
            "access_token": access_token,
            "token_type": "Bearer",
            "user": usuario.to_dict(),
        }
    ), 200


@auth_bp.get("/me")
@jwt_required()
def current_user():
    """
    Retorna la información del usuario asociado al token JWT.
    """
    usuario_id = get_jwt_identity()
    claims = get_jwt()

    try:
        usuario_id = int(usuario_id)
    except (TypeError, ValueError):
        return jsonify(
            {
                "error": "invalid_token_identity",
                "message": "La identidad del token no es válida",
            }
        ), 401

    usuario = db.session.get(
        Usuario,
        usuario_id,
    )

    if usuario is None or not usuario.activo:
        return jsonify(
            {
                "error": "user_not_available",
                "message": (
                    "El usuario no existe o se encuentra inactivo"
                ),
            }
        ), 401

    return jsonify(
        {
            "user": usuario.to_dict(),
            "token": {
                "rol": claims.get("rol"),
                "nombre": claims.get("nombre"),
            },
        }
    ), 200