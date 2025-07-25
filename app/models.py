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


