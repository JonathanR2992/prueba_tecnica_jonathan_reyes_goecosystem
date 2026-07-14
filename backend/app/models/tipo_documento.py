from app.extensions import db


class TipoDocumento(db.Model):
    __tablename__ = "tipos_documento"

    codigo = db.Column(
        db.String(3),
        primary_key=True,
    )

    nombre = db.Column(
        db.String(50),
        nullable=False,
        unique=True,
    )

    activo = db.Column(
        db.Boolean,
        nullable=False,
        default=True,
    )

    pacientes = db.relationship(
        "Paciente",
        back_populates="tipo_documento_rel",
        lazy="dynamic",
    )

    def to_dict(self) -> dict:
        return {
            "codigo": self.codigo,
            "nombre": self.nombre,
            "activo": self.activo,
        }