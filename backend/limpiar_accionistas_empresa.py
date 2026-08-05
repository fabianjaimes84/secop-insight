#!/usr/bin/env python3
"""
Script para limpiar la tabla accionistas_empresa.
Remover columnas de datos personales que están duplicadas (estan en personas).
Mantener solo: id, empresa_id, persona_id, nombre, cedula, orden, porcentaje, es_representante_legal
"""

import sqlite3

DB_PATH = "secop.db"

def limpiar_accionistas():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        print("[*] Iniciando limpieza de tabla accionistas_empresa...")
        print()

        # Crear tabla temporal con estructura limpia
        print("[*] Creando tabla temporal con estructura limpia...")
        cursor.execute("""
            CREATE TABLE accionistas_empresa_new (
                id INTEGER PRIMARY KEY,
                empresa_id INTEGER NOT NULL,
                persona_id INTEGER,
                nombre VARCHAR DEFAULT '',
                cedula VARCHAR DEFAULT '',
                orden INTEGER DEFAULT 1,
                porcentaje VARCHAR DEFAULT '',
                es_representante_legal BOOLEAN DEFAULT 0,
                FOREIGN KEY(empresa_id) REFERENCES empresas(id),
                FOREIGN KEY(persona_id) REFERENCES personas(id)
            )
        """)
        print("[OK] Tabla temporal creada")

        # Copiar datos esenciales
        print("[*] Copiando datos esenciales...")
        cursor.execute("""
            INSERT INTO accionistas_empresa_new
            (id, empresa_id, persona_id, nombre, cedula, orden, porcentaje, es_representante_legal)
            SELECT id, empresa_id, persona_id, nombre, cedula, orden, porcentaje, es_representante_legal
            FROM accionistas_empresa
        """)
        print(f"[OK] {cursor.rowcount} registros copiados")

        # Remover tabla antigua
        print("[*] Removiendo tabla antigua...")
        cursor.execute("DROP TABLE accionistas_empresa")
        print("[OK] Tabla antigua removida")

        # Renombrar tabla nueva
        print("[*] Renombrando tabla nueva...")
        cursor.execute("ALTER TABLE accionistas_empresa_new RENAME TO accionistas_empresa")
        print("[OK] Tabla renombrada")

        conn.commit()
        print()
        print("[OK] Limpieza completada exitosamente!")
        print()
        print("Columnas removidas:")
        print("  - cedula_ciudad")
        print("  - mat_profe")
        print("  - direccion_personal")
        print("  - ciudad_personal")
        print("  - correo_personal")
        print("  - telefono_personal_fijo")
        print("  - telefono_personal_celular")
        print()
        print("Columnas mantenidas:")
        print("  - id, empresa_id, persona_id, nombre, cedula")
        print("  - orden, porcentaje, es_representante_legal")

        conn.close()

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    limpiar_accionistas()
