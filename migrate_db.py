#!/usr/bin/env python3
"""
Script de Migración para Base de Datos PostgreSQL

Este script conecta a la base de datos PostgreSQL y ejecuta las migraciones necesarias
para crear o actualizar la estructura de la base de datos.
"""

import os
import sys
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv

# Cargar variables de entorno si existe un archivo .env
load_dotenv()

# Cadena de conexión a la base de datos
DB_CONNECTION_STRING = "postgresql://financialfamilydb_user:F2HOFqnniRHbPuH3nAtzERM9QqqMuHHF@dpg-cv7q408fnakc73dsosqg-a.oregon-postgres.render.com/financialfamilydb"

# Definición de tablas
TABLES = {
    "families": """
    CREATE TABLE IF NOT EXISTS families (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        code VARCHAR(20) UNIQUE NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    """,
    
    "members": """
    CREATE TABLE IF NOT EXISTS members (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        telegram_id VARCHAR(100) UNIQUE,
        family_id INTEGER REFERENCES families(id) ON DELETE CASCADE,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    """,
    
    "expenses": """
    CREATE TABLE IF NOT EXISTS expenses (
        id SERIAL PRIMARY KEY,
        description VARCHAR(255) NOT NULL,
        amount DECIMAL(10, 2) NOT NULL,
        paid_by INTEGER REFERENCES members(id) ON DELETE CASCADE,
        family_id INTEGER REFERENCES families(id) ON DELETE CASCADE,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    """,
    
    "payments": """
    CREATE TABLE IF NOT EXISTS payments (
        id SERIAL PRIMARY KEY,
        from_member INTEGER REFERENCES members(id) ON DELETE CASCADE,
        to_member INTEGER REFERENCES members(id) ON DELETE CASCADE,
        amount DECIMAL(10, 2) NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        CONSTRAINT check_different_members CHECK (from_member != to_member)
    );
    """
}

def create_tables(conn):
    """
    Crea las tablas definidas en el diccionario TABLES si no existen.
    
    Args:
        conn: Conexión a la base de datos
    """
    print("Creando tablas...")
    with conn.cursor() as cur:
        for table_name, table_sql in TABLES.items():
            print(f"Creando tabla '{table_name}' si no existe...")
            cur.execute(table_sql)
    conn.commit()
    print("Tablas creadas correctamente.")

def create_indexes(conn):
    """
    Crea índices para mejorar el rendimiento de consultas comunes.
    
    Args:
        conn: Conexión a la base de datos
    """
    print("Creando índices...")
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_members_family_id ON members(family_id);",
        "CREATE INDEX IF NOT EXISTS idx_expenses_family_id ON expenses(family_id);",
        "CREATE INDEX IF NOT EXISTS idx_expenses_paid_by ON expenses(paid_by);",
        "CREATE INDEX IF NOT EXISTS idx_payments_from_member ON payments(from_member);",
        "CREATE INDEX IF NOT EXISTS idx_payments_to_member ON payments(to_member);",
    ]
    
    with conn.cursor() as cur:
        for index_sql in indexes:
            cur.execute(index_sql)
    conn.commit()
    print("Índices creados correctamente.")

def add_version_table(conn):
    """
    Crea una tabla para gestionar versiones de la base de datos.
    
    Args:
        conn: Conexión a la base de datos
    """
    print("Creando tabla de versiones...")
    version_table_sql = """
    CREATE TABLE IF NOT EXISTS db_version (
        id SERIAL PRIMARY KEY,
        version VARCHAR(20) NOT NULL,
        applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    with conn.cursor() as cur:
        cur.execute(version_table_sql)
        
        # Verificar si ya hay una versión en la tabla
        cur.execute("SELECT COUNT(*) FROM db_version;")
        count = cur.fetchone()[0]
        
        if count == 0:
            # Insertar la versión inicial
            cur.execute("INSERT INTO db_version (version) VALUES (%s);", ("1.0.0",))
            
    conn.commit()
    print("Tabla de versiones creada y actualizada correctamente.")

def main():
    """
    Función principal que ejecuta las migraciones.
    """
    try:
        # Intentar conectar a la base de datos
        print(f"Conectando a la base de datos...")
        conn = psycopg2.connect(DB_CONNECTION_STRING)
        
        # Crear tablas
        create_tables(conn)
        
        # Crear índices
        create_indexes(conn)
        
        # Añadir tabla de versiones
        add_version_table(conn)
        
        # Cerrar conexión
        conn.close()
        print("Migración completada exitosamente.")
        
    except Exception as e:
        print(f"Error durante la migración: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 