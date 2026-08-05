#!/usr/bin/env python3
"""
Script para remover tabla personas y campo persona_id de accionistas_empresa.
"""

import sqlite3

DB_PATH = "secop.db"

def limpiar():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        print("[*] Iniciando limpieza...")
        print()

        # 1. Remover tabla personas
        print("[*] Removiendo tabla personas...")
        cursor.execute("DROP TABLE IF EXISTS personas")
        print("[OK] Tabla personas removida")

        # 2. Recrear accionistas_empresa sin persona_id
        print("[*] Recreando accionistas_empresa sin persona_id...")
        cursor.execute("""
            CREATE TABLE accionistas_empresa_new (
                id INTEGER PRIMARY KEY,
                empresa_id INTEGER NOT NULL,
                nombre VARCHAR DEFAULT '',
                cedula VARCHAR DEFAULT '',
                orden INTEGER DEFAULT 1,
                porcentaje VARCHAR DEFAULT '',
                es_representante_legal BOOLEAN DEFAULT 0,
                FOREIGN KEY(empresa_id) REFERENCES empresas(id)
            )
        """)

        cursor.execute("""
            INSERT INTO accionistas_empresa_new
            (id, empresa_id, nombre, cedula, orden, porcentaje, es_representante_legal)
            SELECT id, empresa_id, nombre, cedula, orden, porcentaje, es_representante_legal
            FROM accionistas_empresa
        """)

        cursor.execute("DROP TABLE accionistas_empresa")
        cursor.execute("ALTER TABLE accionistas_empresa_new RENAME TO accionistas_empresa")
        print("[OK] Tabla accionistas_empresa limpia (sin persona_id)")

        conn.commit()
        print()
        print("[OK] Limpieza completada!")
        print()
        print("Cambios:")
        print("  - Tabla personas: REMOVIDA")
        print("  - Campo persona_id: REMOVIDO de accionistas_empresa")

        conn.close()

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    limpiar()
