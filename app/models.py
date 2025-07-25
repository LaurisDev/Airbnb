import psycopg2

def get_db_connection():
    conn = psycopg2.connect(
        host="ep-dry-tooth-aerlqbqo-pooler.c-2.us-east-2.aws.neon.tech",
        database="neondb",
        user="neondb_owner",
        password="npg_8LxDvgSh2Rfo"
    )
    return conn

def obtener_alojamientos():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT titulo, descripcion, precio_por_noche, imagen_principal, puntuacion FROM alojamientos")
    alojamientos = cur.fetchall()
    cur.close()
    conn.close()
    return alojamientos

def obtener_alojamientos_filtrados(location, checkin, checkout, guests):
    conn = get_db_connection()
    cur = conn.cursor()
    query = """
        SELECT titulo, descripcion, precio_por_noche, imagen_principal, puntuacion
        FROM alojamientos
        WHERE ubicacion ILIKE %s
          AND fecha_disponible_desde <= %s
          AND fecha_disponible_hasta >= %s
          AND capacidad >= %s
    """
    cur.execute(query, (f"%{location}%", checkin, checkout, guests))
    alojamientos = cur.fetchall()
    cur.close()
    conn.close()
    return alojamientos


# ----------------------------------------------------------------------------------------------------
#PARTE DEL REGISTRO DE USUARIOS
def registrar_usuario (nombre, apellidos, email, telefono, contraseña):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO usuarios (nombre, apellidos, email, telefono, contraseña)
            VALUES (%s, %s, %s, %s, %s)
        """, (nombre, apellidos, email, telefono, contraseña))
        conn.commit()
    except Exception as e: #capturo la exepcion y la guardo en la variable e
        conn.rollback()    # por si hay un error, anula la operacion mejo
        raise e            
    finally:
        cur.close()
        conn.close()
# ----------------------------------------------------------------------------------------------------

#para el registro necesitamos verificar si el usuario ya existe
def verificar_usuario_existente(email):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
    resultado = cursor.fetchone()
    cursor.close()
    conn.close()
    return resultado is not None



