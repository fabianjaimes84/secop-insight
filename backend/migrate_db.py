#!/usr/bin/env python3
"""
Script para migrar la BD de la estructura antigua a la nueva.
Agrega columnas nuevas y remueve las antiguas de la tabla empresas.
"""

import sqlite3
import os

DB_PATH = "secop.db"

def migrate():
    if not os.path.exists(DB_PATH):
        print(f"[!] BD no encontrada en {DB_PATH}")
        return False

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        print("[*] Iniciando migracion de BD...")

        # Crear tabla temporal con la nueva estructura
        cursor.execute("""
            CREATE TABLE empresas_new (
                id INTEGER PRIMARY KEY,
                nom_o_raz_social VARCHAR NOT NULL UNIQUE,
                nit VARCHAR DEFAULT '',
                es_persona_juridica BOOLEAN DEFAULT 0,
                direccion VARCHAR DEFAULT '',
                ciudad VARCHAR DEFAULT '',
                correo VARCHAR DEFAULT '',
                telefono_fijo VARCHAR DEFAULT '',
                telefono_celular VARCHAR DEFAULT '',
                contador_id INTEGER,
                FOREIGN KEY(contador_id) REFERENCES contadores(id)
            )
        """)
        print("[OK] Tabla temporal creada")

        # Copiar datos de la tabla antigua (sin los campos que se removieron)
        cursor.execute("""
            INSERT INTO empresas_new
            (id, nom_o_raz_social, nit, es_persona_juridica, contador_id)
            SELECT id, nom_o_raz_social, nit, es_persona_juridica, contador_id
            FROM empresas
        """)
        print(f"[OK] {cursor.rowcount} empresas migradas")

        # Remover tabla antigua
        cursor.execute("DROP TABLE empresas")
        print("[OK] Tabla antigua removida")

        # Renombrar tabla nueva
        cursor.execute("ALTER TABLE empresas_new RENAME TO empresas")
        print("[OK] Tabla renombrada")

        # Agregar columnas nuevas a AccionistaEmpresa
        cursor.execute("PRAGMA table_info(accionistas_empresa)")
        columns = [col[1] for col in cursor.fetchall()]

        new_accionista_columns = [
            'cedula_ciudad',
            'mat_profe',
            'direccion_personal',
            'ciudad_personal',
            'correo_personal',
            'telefono_personal_fijo',
            'telefono_personal_celular',
            'es_representante_legal'
        ]

        for col in new_accionista_columns:
            if col not in columns:
                cursor.execute(f"ALTER TABLE accionistas_empresa ADD COLUMN {col} VARCHAR DEFAULT ''")
                print(f"[OK] Columna {col} agregada a accionistas_empresa")

        # Agregar es_representante_legal si es BOOLEAN
        cursor.execute("PRAGMA table_info(accionistas_empresa)")
        accionista_cols = [col[1] for col in cursor.fetchall()]

        if 'is_representante_legal' not in accionista_cols:
            cursor.execute("ALTER TABLE accionistas_empresa ADD COLUMN is_representante_legal BOOLEAN DEFAULT 0")
            print("[OK] Columna is_representante_legal agregada")
        else:
            print("[INFO] Columna is_representante_legal ya existe")

        # Agregar columnas nuevas a ProponentePerfil
        cursor.execute("PRAGMA table_info(proponentes_perfil)")
        columns = [col[1] for col in cursor.fetchall()]

        new_proponente_columns = {
            'repre_principal_accionista_id': 'INTEGER',
            'repre_suplente_accionista_id': 'INTEGER',
            'experiencia_requerida': 'VARCHAR',
            'poliza_numero': 'VARCHAR',
            'poliza_vigencia': 'VARCHAR',
            'poliza_valor': 'FLOAT',
            'entidad_correo': 'VARCHAR',
            'entidad_url_web': 'VARCHAR',
            'entidad_url_politica_datos': 'VARCHAR'
        }

        for col, col_type in new_proponente_columns.items():
            if col not in columns:
                cursor.execute(f"ALTER TABLE proponentes_perfil ADD COLUMN {col} {col_type} DEFAULT ''")
                print(f"[OK] Columna {col} agregada a proponentes_perfil")

        # Renombrar entidad_pagina a entidad_url_web si entidad_pagina existe
        if 'entidad_pagina' in columns:
            print("[INFO] Columna entidad_pagina ya existe, no se necesita renombar")

        # Renombrar entidad_politica a entidad_url_politica_datos si entidad_politica existe
        if 'entidad_politica' in columns:
            print("[INFO] Columna entidad_politica ya existe, no se necesita renombar")

        conn.commit()
        print("\n[OK] Migracion completada exitosamente!")
        return True

    except sqlite3.OperationalError as e:
        print(f"[ERROR] Error de migracion: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Error inesperado: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    success = migrate()
    exit(0 if success else 1)
