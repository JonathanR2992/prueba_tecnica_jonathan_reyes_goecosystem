from app.extensions import db


class Paciente(db.Model):
    __tablename__ = "pacientes"

    paciente_id = db.Column(
        db.BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    tipo_documento = db.Column(
        db.String(3),
        db.ForeignKey(
            "tipos_documento.codigo",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    documento = db.Column(
        db.String(20),
        nullable=False,
        unique=True,
    )

    nombre_completo = db.Column(
        db.String(150),
        nullable=False,
    )

    fecha_nacimiento = db.Column(
        db.Date,
        nullable=False,
    )

    genero = db.Column(
        db.String(30),
        db.ForeignKey(
            "generos.nombre",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    telefono = db.Column(
        db.String(20),
        nullable=False,
    )

    correo = db.Column(
        db.String(150),
        nullable=True,
    )

    eps_codigo = db.Column(
        db.String(10),
        db.ForeignKey(
            "eps.eps_codigo",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    ciudad = db.Column(
        db.String(80),
        nullable=True,
    )

    prioridad = db.Column(
        db.String(10),
        db.ForeignKey(
            "prioridades.nombre",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    estado = db.Column(
        db.String(20),
        db.ForeignKey(
            "estados.nombre",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    fecha_creacion = db.Column(
        db.DateTime,
        nullable=False,
    )

    fecha_actualizacion = db.Column(
        db.DateTime,
        nullable=False,
    )

    tipo_documento_rel = db.relationship(
        "TipoDocumento",
        back_populates="pacientes",
    )

    genero_rel = db.relationship(
        "Genero",
        back_populates="pacientes",
    )

    eps_rel = db.relationship(
        "Eps",
        back_populates="pacientes",
    )

    prioridad_rel = db.relationship(
        "Prioridad",
        back_populates="pacientes",
    )

    estado_rel = db.relationship(
        "Estado",
        back_populates="pacientes",
    )

    def to_dict(self) -> dict:
        return {
            "paciente_id": self.paciente_id,
            "tipo_documento": self.tipo_documento,
            "tipo_documento_nombre": (
                self.tipo_documento_rel.nombre
                if self.tipo_documento_rel
                else None
            ),
            "documento": self.documento,
            "nombre_completo": self.nombre_completo,
            "fecha_nacimiento": (
                self.fecha_nacimiento.isoformat()
                if self.fecha_nacimiento
                else None
            ),
            "genero": self.genero,
            "telefono": self.telefono,
            "correo": self.correo,
            "eps_codigo": self.eps_codigo,
            "eps_nombre": (
                self.eps_rel.eps_nombre
                if self.eps_rel
                else None
            ),
            "ciudad": self.ciudad,
            "prioridad": self.prioridad,
            "estado": self.estado,
            "fecha_creacion": (
                self.fecha_creacion.isoformat()
                if self.fecha_creacion
                else None
            ),
            "fecha_actualizacion": (
                self.fecha_actualizacion.isoformat()
                if self.fecha_actualizacion
                else None
            ),
        }