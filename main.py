import psycopg2
from typing import List, Tuple
from sentence_transformers import SentenceTransformer 
import numpy as np
import time
import os
from dotenv import load_dotenv

load_dotenv()  # Carga variables del .env

# --- 1. Configuración de la Conexión y Modelo ---
DB_NAME = os.getenv("POSTGRES_DB")
DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_HOST = os.getenv("POSTGRES_HOST", "127.0.0.1")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")

VECTOR_DIM = 384  
MODEL_NAME = 'all-MiniLM-L6-v2' 

# Carga el modelo de IA una sola vez al inicio
print(f"Cargando modelo de embeddings: {MODEL_NAME}...")
embendding_model = SentenceTransformer(MODEL_NAME)
print("Modelo cargado exitosamente.")

# --- 2. Funciones de Conexión y Setup ---

def connect_db():
    """Establece y devuelve una conexión a la base de datos."""
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        print("Conexión exitosa a PostgreSQL.")
        return conn
    except Exception as e:
        # LOG DE ERROR CRÍTICO DE CONEXIÓN
        print(f"\n[ERROR CRÍTICO: CONEXIÓN] No se pudo conectar a la base de datos.")
        print(f"  Asegúrate que Docker esté corriendo y la contraseña '{DB_PASSWORD}' sea correcta.")
        print(f"  Razón de psycopg2: {e}")
        return None
    

def ensure_vector_extension(conn):
    """Asegura que la extensión pgvector esté instalada en la base de datos."""
    try:
        with conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            conn.commit()
        print("Extensión 'vector' verificada/creada exitosamente.")
    except Exception as e:
        # LOG DE ERROR DE EXTENSIÓN
        print(f"[ERROR: EXTENSIÓN] Falló la creación/verificación de la extensión 'vector'.")
        print(f"  Razón: {e}")
        conn.rollback()

def setup_db(conn):
    """Verifica y recrea la tabla con la dimensión correcta si es necesario."""
    try: 
        with conn.cursor() as cur:
            # Eliminamos la tabla para asegurar la correcta dimensión 384
            cur.execute("DROP TABLE IF EXISTS items;")
            
            # La sentencia CREATE TABLE: content y embedding VECTOR(384)
            cur.execute(f"""
                CREATE TABLE items (
                    id SERIAL PRIMARY KEY,
                    content TEXT NOT NULL,
                    embedding VECTOR({VECTOR_DIM})
                );
            """) 
            conn.commit()
        print(f"Tabla 'items' (VECTOR({VECTOR_DIM})) creada exitosamente.") 
    except Exception as e:
        # LOG DE ERROR DE CONFIGURACIÓN DE TABLA
        print(f"[ERROR: SETUP DB] Falló la creación/eliminación de la tabla.")
        print(f"  Razón: {e}")
        conn.rollback() 

# --- 3. Funciones de Inserción (Asignación Numérica Real) ---

def insert_data(conn, description: str, vector: List[float]):
    """Inserta el vector (ya generado) en la tabla 'items'."""
    try:
        # CONVERSIÓN CRÍTICA: Lista de Python a formato String PostgreSQL [n1, n2, ...]
        vector_str = "[" + ",".join(map(str, vector)) + "]"
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO items (content, embedding) VALUES (%s, %s)",
                (description, vector_str) 
            )
            conn.commit()
        print(f"  [+] Insertado: '{description[:40]}...'")
    except Exception as e:
        # LOG DE ERROR DE INSERCIÓN
        print(f"[ERROR: INSERCIÓN] Falló la inserción del dato '{description[:30]}...'.")
        print(f"  Razón: {e}")
        conn.rollback()
    
def process_and_insert(conn, text_data: str):
    """Toma texto, genera el embedding con la IA (la asignación numérica) y lo almacena."""
    
    # 1. ASIGNACIÓN: La IA convierte el significado del texto a 384 números
    vector_array = embendding_model.encode(text_data)
    
    # 2. CONVERSIÓN: De array NumPy a lista de Python
    vector_list = vector_array.tolist()
    
    # 3. Guardar en la Base de Datos
    insert_data(conn, text_data, vector_list)
    
# --- 4. Función de Búsqueda (Similitud Vectorial) ---
    
def find_most_similar(conn, query_text: str, limit: int = 2):
    """Busca los elementos más similares usando el operador <->."""
    print("-" * 50)
    print(f"INICIANDO BÚSQUEDA VECTORIAL para: '{query_text}'")

    # 1. Generar el vector de la consulta
    query_vector_array = embendding_model.encode(query_text)
    query_vector_list = query_vector_array.tolist()

    # 2. Formatear el vector de consulta a string SQL
    query_vector_str = "[" + ",".join(map(str, query_vector_list)) + "]"
    
    start_time = time.time()
    
    try:
        with conn.cursor() as cur:
            # LA CONSULTA CLAVE: Operador <-> y ORDER BY distance ASC
            cur.execute(f"""
                SELECT 
                    content,  
                    embedding <-> '{query_vector_str}' AS distance 
                FROM items 
                ORDER BY distance ASC
                LIMIT %s;
            """, (limit,))
            
            results = cur.fetchall()
            end_time = time.time()
            
            print(f"Consulta completada en {end_time - start_time:.4f} segundos.")
            print("--- Resultados (Menor distancia = Mayor Similitud) ---")
            for content, distance in results:
                print(f"  - Contenido: {content}")
                print(f"    Distancia (Similitud): {distance:.6f}") 
            print("-" * 50)
            
    except Exception as e:
        # LOG DE ERROR DE BÚSQUEDA
        print(f"[ERROR: BÚSQUEDA] Falló la consulta de similitud.")
        print(f"  Razón: {e}")
    
# --- 5. Bloque Principal de Ejecución ---

if __name__ == "__main__":
    conn = connect_db()
    
    if conn:
        print("\n--- INICIO DE PROCESAMIENTO ---")
        
        ensure_vector_extension(conn)
        setup_db(conn)
        
        # FASE DE INSERCIÓN
        print("\n--- Insertando Datos de Prueba ---")
        process_and_insert(conn, "Un plátano amarillo maduro, perfecto para un batido o postre.")
        process_and_insert(conn, "Manzanas rojas y verdes cultivadas en el campo.")
        process_and_insert(conn, "El cohete fue lanzado con éxito hacia Marte.")
        process_and_insert(conn, "La computadora portátil tiene un procesador rápido.")
        process_and_insert(conn, "PostgreSQL es la base de datos relacional más avanzada para escalabilidad.")
        
        
        # FASE DE BÚSQUEDA
        
        # Consulta 1: Prueba de Tecnología
        query_tech = "Necesito comprar un nuevo software o hardware para desarrollar."
        find_most_similar(conn, query_tech, limit=3)
        
        # Consulta 2: Prueba de Comida
        query_food = "Necesito hacer un batido."
        find_most_similar(conn, query_food, limit=3)
        
        #consulta 3: Prueba DB
        query_db = "¿Cuál es la base de datos relacional más avanzada?"
        find_most_similar(conn, query_db, limit=3)
        
        conn.close()
        print("\n[FIN] Conexión cerrada. ¡Bootcamp completado!")
    else:

        print("\n[FIN] El programa no pudo iniciar sin una conexión exitosa a la base de datos.")
