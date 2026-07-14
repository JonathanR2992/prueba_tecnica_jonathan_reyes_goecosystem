from app.extensions import db


class Prioridad(db.Model):
    __tablename__ = "prioridades"

    nombre = db.Column(
        db.String(10),
        primary_key=True,
    )

    nivel = db.Column(
        db.SmallInteger,
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
        back_populates="prioridad_rel",
        lazy="dynamic",
    )

    def to_dict(self) -> dict:
        return {
            "nombre": self.nombre,
            "nivel": self.nivel,
            "activo": self.activo,
        }