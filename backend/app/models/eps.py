from app.extensions import db


class Eps(db.Model):
    __tablename__ = "eps"

    eps_codigo = db.Column(
        db.String(10),
        primary_key=True,
    )

    eps_nombre = db.Column(
        db.String(100),
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
        back_populates="eps_rel",
        lazy="dynamic",
    )

    def to_dict(self) -> dict:
        return {
            "eps_codigo": self.eps_codigo,
            "eps_nombre": self.eps_nombre,
            "activo": self.activo,
        }