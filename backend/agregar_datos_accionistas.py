"""
Migración: Agregar campos de contacto y matrícula profesional a accionistas.
"""

from sqlalchemy import text
from app.db.base import SessionLocal, engine

def agregar_columnas():
    """Agrega las nuevas columnas a la tabla accionistas_empresa."""

    db = SessionLocal()

    columnas_a_agregar = [
        ("direccion", "VARCHAR DEFAULT ''"),
        ("email", "VARCHAR DEFAULT ''"),
        ("telefono", "VARCHAR DEFAULT ''"),
        ("tiene_matricula_profesional", "BOOLEAN DEFAULT FALSE"),
        ("matricula_profesional", "VARCHAR DEFAULT ''"),
    ]

    try:
        for col_name, col_type in columnas_a_agregar:
            try:
                # Intentar agregar la columna
                sql = f"ALTER TABLE accionistas_empresa ADD COLUMN {col_name} {col_type}"
                db.execute(text(sql))
                print(f"✓ Columna '{col_name}' agregada exitosamente")
            except Exception as e:
                if "already exists" in str(e):
                    print(f"⊘ Columna '{col_name}' ya existe")
                else:
                    print(f"✗ Error al agregar '{col_name}': {e}")

        db.commit()
        print("\n✓ Migración completada")

    except Exception as e:
        print(f"✗ Error durante la migración: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 80)
    print("MIGRACIÓN: Agregar datos de contacto y matrícula a accionistas")
    print("=" * 80)
    print()
    agregar_columnas()
