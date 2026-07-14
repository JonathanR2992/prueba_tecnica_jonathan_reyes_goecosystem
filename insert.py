from pathlib import Path

import pandas as pd
import pymysql


ARCHIVO_ODS = Path("Datos_Sinteticos_Prueba_Full_Stack_Junior_2026.ods")
HOJA_PACIENTES = 0

DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "123",
    "database": "goecosystem",
    "charset": "utf8mb4",
    "autocommit": False,
}


SQL_INSERT = """
INSERT INTO pacientes (
    paciente_id,
    tipo_documento,
    documento,
    nombre_completo,
    fecha_nacimiento,
    genero,
    telefono,
    correo,
    eps_codigo,
    ciudad,
    prioridad,
    estado,
    fecha_creacion,
    fecha_actualizacion
)
VALUES (
    %s, %s, %s, %s, %s, %s, %s,
    %s, %s, %s, %s, %s, %s, %s
)
"""


def leer_archivo() -> pd.DataFrame:
    dataframe = pd.read_excel(
        ARCHIVO_ODS,
        sheet_name=HOJA_PACIENTES,
        engine="odf",
        dtype={
            "tipo_documento": str,
            "documento": str,
            "nombre_completo": str,
            "genero": str,
            "telefono": str,
            "correo": str,
            "eps_codigo": str,
            "eps_nombre": str,
            "ciudad": str,
            "prioridad": str,
            "estado": str,
        },
    )

    dataframe.columns = [
        str(columna).strip().lower()
        for columna in dataframe.columns
    ]

    dataframe = dataframe.dropna(how="all").copy()

    # Se elimina porque el nombre de la EPS está normalizado
    # en la tabla eps.
    dataframe = dataframe.drop(
        columns=["eps_nombre"],
        errors="ignore",
    )

    return dataframe


def limpiar_texto(valor):
    if pd.isna(valor):
        return None

    texto = str(valor).strip()

    if not texto:
        return None

    if texto.endswith(".0"):
        texto = texto[:-2]

    return texto


def preparar_dataframe(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    columnas_requeridas = [
        "paciente_id",
        "tipo_documento",
        "documento",
        "nombre_completo",
        "fecha_nacimiento",
        "genero",
        "telefono",
        "correo",
        "eps_codigo",
        "ciudad",
        "prioridad",
        "estado",
        "fecha_creacion",
        "fecha_actualizacion",
    ]

    faltantes = [
        columna
        for columna in columnas_requeridas
        if columna not in dataframe.columns
    ]

    if faltantes:
        raise ValueError(
            "Faltan columnas obligatorias: "
            + ", ".join(faltantes)
        )

    columnas_texto = [
        "tipo_documento",
        "documento",
        "nombre_completo",
        "genero",
        "telefono",
        "correo",
        "eps_codigo",
        "ciudad",
        "prioridad",
        "estado",
    ]

    for columna in columnas_texto:
        dataframe[columna] = dataframe[columna].apply(
            limpiar_texto
        )

    dataframe["paciente_id"] = pd.to_numeric(
        dataframe["paciente_id"],
        errors="raise",
    ).astype(int)

    dataframe["fecha_nacimiento"] = pd.to_datetime(
        dataframe["fecha_nacimiento"],
        errors="raise",
    ).dt.date

    dataframe["fecha_creacion"] = pd.to_datetime(
        dataframe["fecha_creacion"],
        errors="raise",
    )

    dataframe["fecha_actualizacion"] = pd.to_datetime(
        dataframe["fecha_actualizacion"],
        errors="raise",
    )

    dataframe = dataframe.drop_duplicates(
        subset=["documento"],
        keep="first",
    )

    return dataframe


def construir_registros(
    dataframe: pd.DataFrame,
) -> list[tuple]:
    registros = []

    for fila in dataframe.itertuples(index=False):
        registros.append(
            (
                fila.paciente_id,
                fila.tipo_documento,
                fila.documento,
                fila.nombre_completo,
                fila.fecha_nacimiento,
                fila.genero,
                fila.telefono,
                fila.correo,
                fila.eps_codigo,
                fila.ciudad,
                fila.prioridad,
                fila.estado,
                fila.fecha_creacion.to_pydatetime(),
                fila.fecha_actualizacion.to_pydatetime(),
            )
        )

    return registros


def insertar_pacientes(
    registros: list[tuple],
) -> int:
    conexion = pymysql.connect(**DB_CONFIG)

    try:
        with conexion.cursor() as cursor:
            cantidad = cursor.executemany(
                SQL_INSERT,
                registros,
            )

        conexion.commit()
        return cantidad

    except Exception:
        conexion.rollback()
        raise

    finally:
        conexion.close()


def main() -> None:
    try:
        dataframe = leer_archivo()

        print("Columnas después de eliminar eps_nombre:")
        print(dataframe.columns.tolist())

        dataframe = preparar_dataframe(dataframe)

        print(f"Registros preparados: {len(dataframe)}")
        print(dataframe.head())

        registros = construir_registros(dataframe)

        cantidad = insertar_pacientes(registros)

        print("\nCarga finalizada correctamente")
        print(f"Registros insertados: {cantidad}")

    except FileNotFoundError as error:
        print(f"Archivo no encontrado: {error}")

    except ValueError as error:
        print(f"Error de validación: {error}")

    except pymysql.MySQLError as error:
        print(f"Error de MariaDB: {error}")

    except Exception as error:
        print(f"Error inesperado: {error}")


if __name__ == "__main__":
    main()