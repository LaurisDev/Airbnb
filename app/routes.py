from flask import render_template, request, jsonify, redirect, url_for, flash, session
from app.models import agregar_resena, obtener_alojamientos, obtener_alojamientos_filtrados, obtener_resenas_alojamiento, registrar_usuario, verificar_resena_existente, verificar_usuario_existente, obtener_alojamiento_por_id, obtener_usuario_por_email, crear_reserva, verificar_disponibilidad
from app.models import get_db_connection
from datetime import datetime

def init_routes(app):
    
    @app.route("/", methods=["GET", "POST"])
    def inicio():
        if request.method == "POST":
            if request.get_json():
                data = request.get_json()
                location = data.get("location")
                checkin = data.get("checkin")
                checkout = data.get("checkout")
                guests = data.get("guests")
            else:
                location = request.form.get("location")
                checkin = request.form.get("checkin")
                checkout = request.form.get("checkout")
                guests = request.form.get("guests")

            alojamientos = obtener_alojamientos_filtrados(location, checkin, checkout, guests)
            return jsonify(alojamientos)
        else:
            alojamientos = obtener_alojamientos()
        
        # Obtener información del usuario si está logueado
        usuario_info = None
        if 'usuario_email' in session:
            usuario_info = obtener_usuario_por_email(session['usuario_email'])
            
        return render_template("inicio.html", alojamientos=alojamientos, usuario_info=usuario_info)

#----------------------------------------------------------------------------------------------------
#REGISTRO DE USUARIOS
    @app.route("/registro", methods=["GET", "POST"])
    def registro():
        if request.method == "POST":
            nombre = request.form.get("nombre", "").strip()
            apellidos = request.form.get("apellidos", "").strip()
            email = request.form.get("email", "").strip()
            telefono = request.form.get("telefono", "").strip()
            contraseña = request.form.get("contraseña", "").strip()

            hay_error = False

            if not nombre:
                flash("Debes ingresar tu nombre.", "error_nombre")
                hay_error = True

            if not apellidos:
                flash("Debes ingresar tus apellidos.", "error_apellidos")
                hay_error = True

            if not email:
                flash("Debes ingresar un email válido.", "error_email")
                hay_error = True

            if not telefono:
                flash("Debes ingresar un número de teléfono.", "error_telefono")
                hay_error = True

            if not contraseña:
                flash("Debes ingresar una contraseña.", "error_contraseña")
                hay_error = True

            if hay_error:
                return render_template("registro.html")

            if verificar_usuario_existente(email):
                flash("El email ya está registrado. Intenta con otro.", "error_email")
                return render_template("registro.html")

            registrar_usuario(nombre, apellidos, email, telefono, contraseña)
            flash("Registro exitoso. Ahora puedes iniciar sesión.", "success_registro")
            return redirect(url_for('login'))

        return render_template("registro.html")
#----------------------------------------------------------------------------------------------------
#LOGIN DE USUARIOS
    @app.route("/login", methods=["GET", "POST"])
    def login():
        next_url = request.args.get('next') if request.method == 'GET' else request.form.get('next')  # URL a la que redirigir después del login

        if request.method == 'POST':
            email = request.form.get("email", "").strip()
            contraseña = request.form.get("contraseña", "").strip()

            if not email or not contraseña:
                flash("Debes ingresar tu email y contraseña.", "error_login")
                return render_template("login.html", next=next_url)

            try:
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute("SELECT * FROM usuarios WHERE email = %s AND contraseña = %s", (email, contraseña))
                user = cur.fetchone()
                cur.close()
                conn.close()
            except Exception as e:
                flash("Error en la base de datos.", "error")
                return render_template("login.html", next=next_url)

            if not user:
                flash("Email o contraseña incorrectos.", "error_login")
                return redirect(url_for("login", next=next_url))

            # guardar usuario en sesión
            session['usuario_email'] = user[3]

            flash("Inicio de sesión exitoso.", "success_login")
            return redirect(next_url or url_for('inicio'))  # redirige a la vista deseada o al inicio

        return render_template("login.html", next=next_url)#get



    @app.route("/logout")
    def logout():
        session.clear()
        flash("Has cerrado sesión correctamente.", "success_logout")
        return redirect(url_for("login"))
        
#----------------------------------------------------------------------------------------------------
    @app.route("/alojamiento/<int:alojamiento_id>")
    def detalle_alojamiento(alojamiento_id):
        checkin = request.args.get("checkin", "")
        checkout = request.args.get("checkout", "")
        guests = request.args.get("guests", "")

        alojamiento = obtener_alojamiento_por_id(alojamiento_id)
        if alojamiento is None:
            flash("Alojamiento no encontrado", "error")
            return redirect(url_for('inicio'))
        
        # Obtener reseñas del alojamiento
        resenas = obtener_resenas_alojamiento(alojamiento_id)
        
        # Verificar si el usuario está logueado
        usuario_logueado = 'usuario_email' in session
        
        # Obtener información del usuario si está logueado
        usuario_info = None
        if 'usuario_email' in session:
            usuario_info = obtener_usuario_por_email(session['usuario_email'])
        
        # Obtener calendario del mes
        from app.models import generar_calendario_mes
        calendario = generar_calendario_mes(alojamiento_id)
        
        return render_template("detalle_alojamiento.html", 
                             alojamiento=alojamiento, 
                             checkin=checkin, 
                             checkout=checkout, 
                             guests=guests,
                             resenas=resenas,
                             usuario_logueado=usuario_logueado,
                             usuario_info=usuario_info,
                             calendario=calendario)

    @app.route("/alojamiento/<int:alojamiento_id>/resena", methods=["POST"])
    def agregar_resena_alojamiento(alojamiento_id):
        # Verificar si el usuario está logueado
        if 'usuario_email' not in session:
            flash("Debes iniciar sesión para agregar una reseña.", "error")
            return redirect(url_for('login'))
        
        comentario = request.form.get("comentario", "").strip()
        puntuacion = request.form.get("puntuacion")
        
        if not comentario or not puntuacion:
            flash("Debes completar todos los campos.", "error")
            return redirect(url_for('detalle_alojamiento', alojamiento_id=alojamiento_id))
        
        try:
            puntuacion = int(puntuacion)
            if puntuacion < 1 or puntuacion > 5:
                flash("La puntuación debe estar entre 1 y 5.", "error")
                return redirect(url_for('detalle_alojamiento', alojamiento_id=alojamiento_id))
        except ValueError:
            flash("La puntuación debe ser un número válido.", "error")
            return redirect(url_for('detalle_alojamiento', alojamiento_id=alojamiento_id))
        
        # Obtener el ID del usuario
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id FROM usuarios WHERE email = %s", (session['usuario_email'],))
        usuario = cur.fetchone()
        cur.close()
        conn.close()
        
        if not usuario:
            flash("Error al obtener información del usuario.", "error")
            return redirect(url_for('detalle_alojamiento', alojamiento_id=alojamiento_id))
        
        usuario_id = usuario[0]
        
        # Verificar si el usuario ya ha dejado una reseña para este alojamiento
        if verificar_resena_existente(usuario_id, alojamiento_id):
            flash("Ya has dejado una reseña para este alojamiento.", "error")
            return redirect(url_for('detalle_alojamiento', alojamiento_id=alojamiento_id))
        
        # Agregar la reseña
        try:
            agregar_resena(usuario_id, alojamiento_id, comentario, puntuacion)
            flash("Reseña agregada exitosamente.", "success_resenas")
        except Exception as e:
            flash("Error al agregar la reseña.", "error_resenas")
        
        return redirect(url_for('detalle_alojamiento', alojamiento_id=alojamiento_id))

    @app.route("/alojamiento/<int:alojamiento_id>/agregar-resena")
    def agregar_resena_pagina(alojamiento_id):
        # Verificar si el usuario está logueado
        if 'usuario_email' not in session:
            flash("Debes iniciar sesión para agregar una reseña.", "error")
            return redirect(url_for('login', next=request.url))
        
        # Obtener información del alojamiento
        alojamiento = obtener_alojamiento_por_id(alojamiento_id)
        if alojamiento is None:
            flash("Alojamiento no encontrado", "error")
            return redirect(url_for('inicio'))
        
        # Verificar si el usuario ya ha dejado una reseña para este alojamiento
        usuario = obtener_usuario_por_email(session['usuario_email'])
        if usuario and verificar_resena_existente(usuario[0], alojamiento_id):
            flash("Ya has dejado una reseña para este alojamiento.", "error")
            return redirect(url_for('detalle_alojamiento', alojamiento_id=alojamiento_id))
        
        return render_template("agregar_resena.html", alojamiento=alojamiento)

    @app.route("/alojamiento/<int:alojamiento_id>/resumen-reserva", methods=["GET", "POST"])
    def resumen_reserva(alojamiento_id):
        # Verificar si el usuario está logueado
        if 'usuario_email' not in session:
            flash("Debes iniciar sesión para realizar una reserva.", "error")
            return redirect(url_for('login', next=request.url))
                
        
        if request.method == "POST":
            checkin = request.form.get("checkin")
            checkout = request.form.get("checkout")
            guests = request.form.get("guests")
            
            # Validar que todos los campos estén presentes
            if not checkin or not checkout or not guests:
                flash("Debes completar todos los campos de la reserva.", "error")
                return redirect(url_for('detalle_alojamiento', alojamiento_id=alojamiento_id))
            
            # Obtener información del alojamiento
            alojamiento = obtener_alojamiento_por_id(alojamiento_id)
            if alojamiento is None:
                flash("Alojamiento no encontrado", "error")
                return redirect(url_for('inicio'))
            
            # Calcular el número de noches
            fecha_checkin = datetime.strptime(checkin, '%Y-%m-%d')
            fecha_checkout = datetime.strptime(checkout, '%Y-%m-%d')
            fecha_actual = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            
            # Validar que las fechas no sean pasadas
            if fecha_checkin < fecha_actual:
                flash("No puedes seleccionar una fecha de check-in en el pasado. Por favor, selecciona una fecha futura.", "error")
                return redirect(url_for('detalle_alojamiento', alojamiento_id=alojamiento_id))
            
            if fecha_checkout < fecha_actual:
                flash("No puedes seleccionar una fecha de check-out en el pasado. Por favor, selecciona una fecha futura.", "error")
                return redirect(url_for('detalle_alojamiento', alojamiento_id=alojamiento_id))
            
            noches = (fecha_checkout - fecha_checkin).days
            
            if noches <= 0:
                flash("La fecha de check-out debe ser posterior al check-in.", "error")
                return redirect(url_for('detalle_alojamiento', alojamiento_id=alojamiento_id))
            
            # Validar capacidad del alojamiento
            capacidad_alojamiento = alojamiento[6]  # alojamiento[6] es la capacidad
            if int(guests) > capacidad_alojamiento:
                flash(f"Lo sentimos, este alojamiento solo puede alojar hasta {capacidad_alojamiento} huésped{'es' if capacidad_alojamiento > 1 else ''}.", "error")
                return redirect(url_for('detalle_alojamiento', alojamiento_id=alojamiento_id))
            
            # Calcular el precio total
            precio_por_noche = alojamiento[3]
            precio_total = precio_por_noche * noches
            
            # Obtener información del usuario
            usuario_info = obtener_usuario_por_email(session['usuario_email'])
            
            return render_template("resumen_reserva.html", 
                                 alojamiento=alojamiento,
                                 checkin=checkin,
                                 checkout=checkout,
                                 guests=guests,
                                 noches=noches,
                                 precio_por_noche=precio_por_noche,
                                 precio_total=precio_total,
                                 usuario_info=usuario_info)
        
        # Si es GET, redirigir al detalle del alojamiento
        return redirect(url_for('detalle_alojamiento', alojamiento_id=alojamiento_id))

    @app.route("/alojamiento/<int:alojamiento_id>/procesar-pago", methods=["POST"])
    def procesar_pago(alojamiento_id):
        # Verificar si el usuario está logueado
        if 'usuario_email' not in session:
            flash("Debes iniciar sesión para realizar una reserva.", "error")
            return redirect(url_for('login'))
        
        # Obtener datos del formulario
        checkin = request.form.get("checkin")
        checkout = request.form.get("checkout")
        guests = request.form.get("guests")
        metodo_pago = request.form.get("metodo_pago")
        
        # Validar que todos los campos estén presentes
        if not checkin or not checkout or not guests or not metodo_pago:
            flash("Debes completar todos los campos.", "error")
            return redirect(url_for('resumen_reserva', alojamiento_id=alojamiento_id))
        
        # Obtener información del alojamiento
        alojamiento = obtener_alojamiento_por_id(alojamiento_id)
        if alojamiento is None:
            flash("Alojamiento no encontrado", "error")
            return redirect(url_for('inicio'))
        
        # Calcular el número de noches y precio total
        fecha_checkin = datetime.strptime(checkin, '%Y-%m-%d')
        fecha_checkout = datetime.strptime(checkout, '%Y-%m-%d')
        fecha_actual = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Validar que las fechas no sean pasadas
        if fecha_checkin < fecha_actual:
            flash("No puedes seleccionar una fecha de check-in en el pasado. Por favor, selecciona una fecha futura.", "error")
            return redirect(url_for('detalle_alojamiento', alojamiento_id=alojamiento_id))
        
        if fecha_checkout < fecha_actual:
            flash("No puedes seleccionar una fecha de check-out en el pasado. Por favor, selecciona una fecha futura.", "error")
            return redirect(url_for('detalle_alojamiento', alojamiento_id=alojamiento_id))
        
        noches = (fecha_checkout - fecha_checkin).days
        precio_total = alojamiento[3] * noches
        
        # Validar capacidad del alojamiento
        capacidad_alojamiento = alojamiento[6]  # alojamiento[6] es la capacidad
        if int(guests) > capacidad_alojamiento:
            flash(f"Lo sentimos, este alojamiento solo puede alojar hasta {capacidad_alojamiento} huésped{'es' if capacidad_alojamiento > 1 else ''}.", "error")
            return redirect(url_for('detalle_alojamiento', alojamiento_id=alojamiento_id))
        
        # Verificar disponibilidad
        if not verificar_disponibilidad(alojamiento_id, checkin, checkout):
            flash("Lo sentimos, el alojamiento no está disponible para las fechas seleccionadas.", "error")
            return redirect(url_for('detalle_alojamiento', alojamiento_id=alojamiento_id))
        
        # Obtener el ID del usuario
        usuario = obtener_usuario_por_email(session['usuario_email'])
        if not usuario:
            flash("Error al obtener información del usuario.", "error")
            return redirect(url_for('detalle_alojamiento', alojamiento_id=alojamiento_id))
        
        usuario_id = usuario[0]
        
        try:
            # Crear la reserva en la base de datos
            reserva_id = crear_reserva(usuario_id, alojamiento_id, checkin, checkout, precio_total)
            
            # Guardar datos de la reserva en la sesión para mostrar en la confirmación
            session['reserva_temp'] = {
                'alojamiento': alojamiento,
                'checkin': checkin,
                'checkout': checkout,
                'guests': guests,
                'noches': noches,
                'precio_total': precio_total
            }
            
            # Aquí podrías integrar con un sistema de pago real (Stripe, PayPal, etc.)
            # Por ahora, simulamos que el pago fue exitoso
            
            return redirect(url_for('confirmacion_reserva', reserva_id=reserva_id))
            
        except Exception as e:
            flash("Error al procesar la reserva. Por favor, intenta nuevamente.", "error")
            return redirect(url_for('detalle_alojamiento', alojamiento_id=alojamiento_id))

    @app.route("/reserva/<int:reserva_id>/confirmacion")
    def confirmacion_reserva(reserva_id):
        # Verificar si el usuario está logueado
        if 'usuario_email' not in session:
            flash("Debes iniciar sesión para ver esta página.", "error")
            return redirect(url_for('login'))
        
        # Obtener los datos de la reserva de la sesión temporal
        # En una implementación real, obtendrías esto de la base de datos
        reserva_data = session.get('reserva_temp', {})
        
        if not reserva_data:
            flash("No se encontró información de la reserva.", "error")
            return redirect(url_for('inicio'))
        
        # Obtener información del usuario
        usuario_info = obtener_usuario_por_email(session['usuario_email'])
        
        return render_template("confirmacion_reserva.html", 
                             reserva_id=reserva_id,
                             alojamiento=reserva_data.get('alojamiento'),
                             checkin=reserva_data.get('checkin'),
                             checkout=reserva_data.get('checkout'),
                             guests=reserva_data.get('guests'),
                             noches=reserva_data.get('noches'),
                             precio_total=reserva_data.get('precio_total'),
                             usuario_info=usuario_info)

    @app.route("/mis-reservas")
    def mis_reservas():
        # Verificar si el usuario está logueado
        if 'usuario_email' not in session:
            flash("Debes iniciar sesión para ver tus reservas.", "error")
            return redirect(url_for('login'))
        
        # Obtener el ID del usuario
        usuario = obtener_usuario_por_email(session['usuario_email'])
        if not usuario:
            flash("Error al obtener información del usuario.", "error")
            return redirect(url_for('inicio'))
        
        usuario_id = usuario[0]
        
        # Obtener las reservas del usuario
        from app.models import obtener_reservas_usuario
        reservas = obtener_reservas_usuario(usuario_id)
        
        return render_template("mis_reservas.html", reservas=reservas, usuario_info=usuario)

    @app.route("/cancelar-reserva/<int:reserva_id>", methods=["POST"])
    def cancelar_reserva_route(reserva_id):
        # Verificar si el usuario está logueado
        if 'usuario_email' not in session:
            flash("Debes iniciar sesión para cancelar reservas.", "error")
            return redirect(url_for('login'))
        
        # Obtener el ID del usuario
        usuario = obtener_usuario_por_email(session['usuario_email'])
        if not usuario:
            flash("Error al obtener información del usuario.", "error")
            return redirect(url_for('inicio'))
        
        usuario_id = usuario[0]
        
        # Cancelar la reserva
        from app.models import cancelar_reserva
        if cancelar_reserva(reserva_id, usuario_id):
            flash("Reserva cancelada exitosamente.", "success_reservas")
        else:
            flash("No se pudo cancelar la reserva. Verifica que la reserva te pertenezca.", "error_reservas")
        
        return redirect(url_for('mis_reservas'))
   
  
