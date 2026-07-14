from app.extensions import db


class Genero(db.Model):
    __tablename__ = "generos"

    nombre = db.Column(
        db.String(30),
        primary_key=True,
    )

    activo = db.Column(
        db.Boolean,
        nullable=False,
        default=True,
    )

    pacientes = db.relationship(
        "Paciente",
        back_populates="genero_rel",
        lazy="dynamic",
    )

    def to_dict(self) -> dict:
        return {
            "nombre": self.nombre,
            "activo": self.activo,
        }