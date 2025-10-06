# 🔎 Proyecto: Búsqueda de Similitud Semántica con PGvector 

Este proyecto implementa la Búsqueda Vectorial (Vector Search) 🧠, una técnica avanzada que utiliza modelos de Inteligencia Artificial (IA) para analizar el significado semántico del texto. Permite encontrar contenido relacionado incluso si no comparte palabras clave, utilizando la base de datos PostgreSQL y la extensión pgvector.

# 🌟 Tecnologías Clave 

Categoría | Tecnología | Función en el Proyecto
Base de Datos | PostgreSQL 🐘 | Motor de base de datos relacional principal.
Extensión | pgvector ✨ | Habilita el almacenamiento y la consulta de vectores de alta dimensión.
IA / Embeddings | Sentence Transformers | Librería de Python para generar los vectores numéricos.
Modelo de IA | all-MiniLM-L6-v2 | Convierte el texto en vectores de 384 dimensiones.
Orquestación | Docker 🐳 | Facilita el despliegue aislado de PostgreSQL con la extensión ya instalada.
Lenguaje | Python 3 🐍 | Script principal (main.py) para la lógica de negocio y las consultas.

# 🎯 Alcance y Funcionalidad

El objetivo del proyecto es demostrar el flujo de trabajo completo de una aplicación de Búsqueda Vectorial:

Generación de Vectores: El texto se transforma en un array de números (vector) que captura su esencia semántica.

Almacenamiento: Los vectores se guardan en la columna de tipo VECTOR(384) en PostgreSQL.

Consulta: Cuando se realiza una búsqueda, el texto de la consulta también se convierte en un vector.

Recuperación: Se calcula la distancia vectorial (<->) entre el vector de la consulta y todos los vectores almacenados. Los resultados con la menor distancia son los más similares en significado.

# 🚀 Guía de Instalación y Uso

## Paso 1: Inicializar la Base de Datos con Docker

Asegúrate de que Docker Desktop esté corriendo. Usaremos la contraseña bootcamp_123 para evitar problemas de caché.

  1. Detener y eliminar el contenedor antiguo (si es necesario)
  docker stop pgvector-db && docker rm pgvector-db

  2. Crear e iniciar el contenedor con la contraseña definida
  docker run --name pgvector-db -e POSTGRES_PASSWORD=bootcamp_123 -p 5432:5432 -d ankane/pgvector

## Paso 2: Configurar el Entorno Python 🐍

Ejecuta estos comandos dentro del directorio de tu proyecto en WSL:

  1. Crear y activar el entorno virtual
  python3 -m venv venv
  source venv/bin/activate

  2. Instalar las dependencias necesarias
  pip install psycopg2-binary sentence-transformers numpy

## Paso 3: Ejecutar el Proyecto

Verifica que el archivo main.py contenga la contraseña bootcamp_123 y el host 127.0.0.1. Luego, ejecuta:

  python main.py

El script mostrará la confirmación de la conexión, la inserción de datos y los resultados de las búsquedas semánticas.

# 🧹 Cierre y Limpieza de Servicios

Para liberar recursos (memoria, CPU y el puerto 5432) cuando termines de usar el proyecto:

## Detener el contenedor de PostgreSQL: 🛑 

  docker stop pgvector-db

## Desactivar el entorno virtual de Python: ↩️

  deactivate

## Cerrar completamente el subsistema WSL (opcional, pero recomendado): 🖥️

  wsl --shutdown

(Ejecutar en PowerShell de Windows)
