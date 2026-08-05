#!/usr/bin/env python3
"""
Script para agregar la columna tipo_grupo_empresarial a la tabla integrantes_proponente.
"""

import sqlite3

DB_PATH = "secop.db"

def agregar_columna():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        print("[*] Iniciando migración...")
        print()

        # Verificar si la columna ya existe
        print("[*] Verificando si la columna ya existe...")
        cursor.execute("PRAGMA table_info(integrantes_proponente)")
        columnas = [col[1] for col in cursor.fetchall()]

        if "tipo_grupo_empresarial" in columnas:
            print("[OK] La columna tipo_grupo_empresarial ya existe.")
            conn.close()
            return

        # Agregar la columna
        print("[*] Agregando columna tipo_grupo_empresarial...")
        cursor.execute("""
            ALTER TABLE integrantes_proponente
            ADD COLUMN tipo_grupo_empresarial VARCHAR DEFAULT ''
        """)
        print("[OK] Columna agregada exitosamente")

        conn.commit()
        print()
        print("[OK] Migración completada!")
        print()
        print("Cambios:")
        print("  - Columna tipo_grupo_empresarial agregada a integrantes_proponente")
        print("    (valores posibles: matriz, subsidiaria, filial, subordinada, otro)")

        conn.close()

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    agregar_columna()
