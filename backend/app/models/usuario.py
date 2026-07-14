from app.extensions import db


class Usuario(db.Model):
    __tablename__ = "usuarios"

    usuario_id = db.Column(
        db.BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    usuario = db.Column(
        db.String(50),
        nullable=False,
        unique=True,
    )

    nombre = db.Column(
        db.String(100),
        nullable=False,
    )

    rol = db.Column(
        db.String(20),
        nullable=False,
    )

    activo = db.Column(
        db.Boolean,
        nullable=False,
        default=True,
    )

    password_demo = db.Column(
        db.String(100),
        nullable=False,
    )

    def to_dict(self) -> dict:
        return {
            "usuario_id": self.usuario_id,
            "usuario": self.usuario,
            "nombre": self.nombre,
            "rol": self.rol,
            "activo": self.activo,
        }