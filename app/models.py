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
    cur.execute("SELECT id, nombre, apellidos FROM usuarios WHERE email = %s", (email,))
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

def obtener_reservas_usuario(usuario_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT r.id, r.fecha_inicio, r.fecha_fin, r.total, r.estado,
               a.titulo, a.imagen_principal, a.precio_por_noche, a.id as alojamiento_id
        FROM reservas r
        JOIN alojamientos a ON r.alojamiento_id = a.id
        WHERE r.usuario_id = %s
        ORDER BY r.fecha_inicio DESC
    """, (usuario_id,))
    reservas = cur.fetchall()
    cur.close()
    conn.close()
    return reservas

def cancelar_reserva(reserva_id, usuario_id):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # Verificar que la reserva pertenece al usuario
        cur.execute("""
            SELECT id FROM reservas 
            WHERE id = %s AND usuario_id = %s
        """, (reserva_id, usuario_id))
        reserva = cur.fetchone()
        
        if not reserva:
            return False
        
        # Actualizar el estado de la reserva a cancelada
        cur.execute("""
            UPDATE reservas 
            SET estado = 'cancelada' 
            WHERE id = %s
        """, (reserva_id,))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()

def obtener_reserva_por_id(reserva_id, usuario_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT r.id, r.fecha_inicio, r.fecha_fin, r.total, r.estado,
               a.titulo, a.imagen_principal, a.precio_por_noche, a.id as alojamiento_id
        FROM reservas r
        JOIN alojamientos a ON r.alojamiento_id = a.id
        WHERE r.id = %s AND r.usuario_id = %s
    """, (reserva_id, usuario_id))
    reserva = cur.fetchone()
    cur.close()
    conn.close()
    return reserva

def obtener_fechas_disponibles(alojamiento_id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Obtener las fechas ocupadas
    cur.execute("""
        SELECT fecha_inicio, fecha_fin
        FROM reservas 
        WHERE alojamiento_id = %s AND estado != 'cancelada'
        ORDER BY fecha_inicio
    """, (alojamiento_id,))
    
    fechas_ocupadas = cur.fetchall()
    cur.close()
    conn.close()
    
    return fechas_ocupadas

def generar_calendario_mes(alojamiento_id):
    from datetime import datetime, date, timedelta
    import calendar
    
    # Obtener el mes actual
    hoy = date.today()
    año_actual = hoy.year
    mes_actual = hoy.month
    
    # Obtener las fechas ocupadas
    fechas_ocupadas = obtener_fechas_disponibles(alojamiento_id)
    
    # Crear calendario
    cal = calendar.monthcalendar(año_actual, mes_actual)
    
    # Convertir fechas ocupadas a set para búsqueda rápida
    fechas_ocupadas_set = set()
    for fecha_inicio, fecha_fin in fechas_ocupadas:
        current_date = fecha_inicio
        while current_date <= fecha_fin:
            fechas_ocupadas_set.add(current_date)
            current_date += timedelta(days=1)
    
    # Generar días del calendario
    dias_calendario = []
    for semana in cal:
        semana_dias = []
        for dia in semana:
            if dia == 0:
                semana_dias.append(None)  # Día vacío
            else:
                fecha_actual = date(año_actual, mes_actual, dia)
                esta_ocupado = fecha_actual in fechas_ocupadas_set
                semana_dias.append({
                    'dia': dia,
                    'fecha': fecha_actual,
                    'ocupado': esta_ocupado,
                    'pasado': fecha_actual < hoy
                })
        dias_calendario.append(semana_dias)
    
    return {
        'año': año_actual,
        'mes': mes_actual,
        'nombre_mes': calendar.month_name[mes_actual],
        'dias': dias_calendario
    }




