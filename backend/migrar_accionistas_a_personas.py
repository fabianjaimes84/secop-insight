#!/usr/bin/env python3
"""
Script para migrar accionistas de accionistas_empresa a personas.
Evita duplicar datos y centraliza todas las personas en una sola tabla.
"""

import sqlite3
from datetime import datetime

DB_PATH = "secop.db"

def migrar_accionistas_a_personas():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        print("[*] Iniciando migración de accionistas a personas...")
        print()

        # 1. Obtener todos los accionistas únicos por cédula
        print("[*] Leyendo accionistas de accionistas_empresa...")
        cursor.execute("""
            SELECT DISTINCT cedula, nombre, cedula_ciudad, mat_profe,
                   direccion_personal, ciudad_personal, correo_personal,
                   telefono_personal_fijo, telefono_personal_celular
            FROM accionistas_empresa
            WHERE cedula != '' AND nombre != ''
            ORDER BY cedula
        """)
        accionistas = cursor.fetchall()
        print(f"   Encontrados {len(accionistas)} accionistas únicos\n")

        # 2. Insertar en tabla personas y guardar mapeo
        mapeo_accionista_persona = {}
        insertados = 0
        duplicados = 0

        print("[*] Insertando accionistas en tabla personas...")
        for cedula, nombre, ciudad, mat, dir_pers, ciudad_pers, correo, tel_fijo, tel_cel in accionistas:
            # Verificar si ya existe en personas
            cursor.execute("SELECT id FROM personas WHERE cedula = ?", (cedula,))
            existente = cursor.fetchone()

            if existente:
                persona_id = existente[0]
                duplicados += 1
                print(f"   [EXISTE] {nombre} ({cedula}) - ya existe en personas (id: {persona_id})")
            else:
                cursor.execute("""
                    INSERT INTO personas
                    (nombre, cedula, cedula_ciudad, mat_profe,
                     direccion_personal, ciudad_personal, correo_personal,
                     telefono_personal_fijo, telefono_personal_celular)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (nombre, cedula, ciudad, mat, dir_pers, ciudad_pers, correo, tel_fijo, tel_cel))
                persona_id = cursor.lastrowid
                insertados += 1
                print(f"   [OK] {nombre} ({cedula}) -> persona_id: {persona_id}")

            mapeo_accionista_persona[cedula] = persona_id

        conn.commit()
        print(f"\n   [OK] Insertados: {insertados}")
        print(f"   [INFO] Ya existian: {duplicados}\n")

        # 3. Actualizar accionistas_empresa con persona_id
        print("[*] Actualizando accionistas_empresa con persona_id...")
        actualizados = 0
        for cedula, persona_id in mapeo_accionista_persona.items():
            cursor.execute("""
                UPDATE accionistas_empresa
                SET persona_id = ?
                WHERE cedula = ?
            """, (persona_id, cedula))
            actualizados += cursor.rowcount

        conn.commit()
        print(f"   [OK] Actualizados: {actualizados} registros\n")

        # 4. Resumen final
        print("[*] Verificacion final...")
        cursor.execute("SELECT COUNT(*) FROM personas")
        total_personas = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM accionistas_empresa WHERE persona_id IS NOT NULL")
        accionistas_vinculados = cursor.fetchone()[0]

        print(f"   Total personas en BD: {total_personas}")
        print(f"   Accionistas vinculados a personas: {accionistas_vinculados}")
        print()

        print("[OK] Migracion completada exitosamente!")
        print()
        print("Proximos pasos (opcional):")
        print("   - Los datos personales en accionistas_empresa se pueden limpiar")
        print("   - Solo usa persona_id para las vinculaciones")

        conn.close()

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    migrar_accionistas_a_personas()
