from flask import render_template, request, jsonify, redirect, url_for, flash, session
from app.models import agregar_resena, obtener_alojamientos, obtener_alojamientos_filtrados, obtener_resenas_alojamiento, registrar_usuario, verificar_resena_existente, verificar_usuario_existente, obtener_alojamiento_por_id
from app.models import get_db_connection

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
            
        return render_template("inicio.html", alojamientos=alojamientos)

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
            flash("Registro exitoso. Ahora puedes iniciar sesión.", "success")
            return redirect(url_for('login'))

        return render_template("registro.html")
#----------------------------------------------------------------------------------------------------
#LOGIN DE USUARIOS
    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == 'POST':
            email = request.form.get("email", "").strip()
            contraseña = request.form.get("contraseña", "").strip()

            if not email or not contraseña:
                flash("Debes ingresar tu email y contraseña.", "error")
                return render_template("login.html")

            try:
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute("SELECT * FROM usuarios WHERE email = %s AND contraseña = %s", (email, contraseña))
                user = cur.fetchone()
                cur.close()
                conn.close()
            except Exception as e:
                flash("Error en la base de datos.", "error")
                return render_template("login.html")

            if not user:
                flash("Email o contraseña incorrectos.", "error")
                return redirect(url_for("login"))

            #  guardar al usuario en sesión 
            session['usuario_email'] = user[3]

            flash("Inicio de sesión exitoso.", "success")
            return redirect(url_for('inicio'))

        return render_template("login.html")


    @app.route("/logout")
    def logout():
        session.clear()
        flash("Has cerrado sesión correctamente.", "success")
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
        
        return render_template("detalle_alojamiento.html", 
                             alojamiento=alojamiento, 
                             checkin=checkin, 
                             checkout=checkout, 
                             guests=guests,
                             resenas=resenas,
                             usuario_logueado=usuario_logueado)

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
            flash("Reseña agregada exitosamente.", "success")
        except Exception as e:
            flash("Error al agregar la reseña.", "error")
        
        return redirect(url_for('detalle_alojamiento', alojamiento_id=alojamiento_id))
   
  
