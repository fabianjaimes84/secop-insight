#!/usr/bin/env python3
"""
Script para agregar columnas de lotes a la tabla proponentes_perfil.
"""

import sqlite3

DB_PATH = "secop.db"

def agregar_columnas():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        print("[*] Iniciando migración de lotes...\n")

        # Verificar si las columnas ya existen
        cursor.execute("PRAGMA table_info(proponentes_perfil)")
        columnas = [col[1] for col in cursor.fetchall()]

        # Agregar presenta_por_lotes si no existe
        if "presenta_por_lotes" not in columnas:
            print("[*] Agregando columna presenta_por_lotes...")
            cursor.execute("""
                ALTER TABLE proponentes_perfil
                ADD COLUMN presenta_por_lotes BOOLEAN DEFAULT 0
            """)
            print("[OK] Columna presenta_por_lotes agregada")
        else:
            print("[OK] Columna presenta_por_lotes ya existe")

        # Agregar lotes_seleccionados si no existe
        if "lotes_seleccionados" not in columnas:
            print("[*] Agregando columna lotes_seleccionados...")
            cursor.execute("""
                ALTER TABLE proponentes_perfil
                ADD COLUMN lotes_seleccionados VARCHAR DEFAULT ''
            """)
            print("[OK] Columna lotes_seleccionados agregada")
        else:
            print("[OK] Columna lotes_seleccionados ya existe")

        conn.commit()
        print("\n[OK] Migración completada!")

        conn.close()

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    agregar_columnas()
