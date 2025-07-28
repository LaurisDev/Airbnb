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
    cur.execute("SELECT id, titulo, descripcion, precio_por_noche, imagen_principal, puntuacion FROM alojamientos")
    alojamientos = cur.fetchall()
    cur.close()
    conn.close()
    return alojamientos

def obtener_alojamientos_filtrados(location, checkin, checkout, guests):
    conn = get_db_connection()
    cur = conn.cursor()
    query = """
        SELECT id, titulo, descripcion, precio_por_noche, imagen_principal, puntuacion
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

def verificar_usuario_existente(email):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
    resultado = cursor.fetchone()
    cursor.close()
    conn.close()
    return resultado is not None


def obtener_alojamiento_por_id(alojamiento_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, titulo, descripcion, precio_por_noche, imagen_principal, puntuacion, capacidad
        FROM alojamientos 
        WHERE id = %s
    """, (alojamiento_id,))
    alojamiento = cur.fetchone()
    cur.close()
    conn.close()
    return alojamiento

def obtener_resenas_alojamiento(alojamiento_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT r.id, r.comentario, r.puntuacion, r.fecha, u.nombre, u.apellidos
        FROM resenas r
        JOIN usuarios u ON r.usuario_id = u.id
        WHERE r.alojamiento_id = %s
        ORDER BY r.fecha DESC
    """, (alojamiento_id,))
    resenas = cur.fetchall()
    cur.close()
    conn.close()
    return resenas

def agregar_resena(usuario_id, alojamiento_id, comentario, puntuacion):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO resenas (usuario_id, alojamiento_id, comentario, puntuacion)
            VALUES (%s, %s, %s, %s)
        """, (usuario_id, alojamiento_id, comentario, puntuacion))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()

def verificar_resena_existente(usuario_id, alojamiento_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id FROM resenas 
        WHERE usuario_id = %s AND alojamiento_id = %s
    """, (usuario_id, alojamiento_id))
    reseña = cur.fetchone()
    cur.close()
    conn.close()
    return reseña is not None

def obtener_usuario_por_email(email):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
    usuario = cur.fetchone()
    cur.close()
    conn.close()
    return usuario

def crear_reserva(usuario_id, alojamiento_id, fecha_inicio, fecha_fin, total):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO reservas (usuario_id, alojamiento_id, fecha_inicio, fecha_fin, total, estado)
            VALUES (%s, %s, %s, %s, %s, 'pendiente')
            RETURNING id
        """, (usuario_id, alojamiento_id, fecha_inicio, fecha_fin, total))
        reserva_id = cur.fetchone()[0]
        conn.commit()
        return reserva_id
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()

def verificar_disponibilidad(alojamiento_id, fecha_inicio, fecha_fin):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT COUNT(*) FROM reservas 
        WHERE alojamiento_id = %s 
        AND estado != 'cancelada'
        AND (
            (fecha_inicio <= %s AND fecha_fin >= %s) OR
            (fecha_inicio <= %s AND fecha_fin >= %s) OR
            (fecha_inicio >= %s AND fecha_fin <= %s)
        )
    """, (alojamiento_id, fecha_inicio, fecha_inicio, fecha_fin, fecha_fin, fecha_inicio, fecha_fin))
    count = cur.fetchone()[0]
    cur.close()
    conn.close()
    return count == 0




