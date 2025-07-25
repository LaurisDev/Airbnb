from flask import render_template, request, jsonify
from app.models import obtener_alojamientos, obtener_alojamientos_filtrados

def init_routes(app):
    @app.route("/", methods=["GET", "POST"])
    def inicio(): 
        if request.method == "POST":
            if request.is_json:
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

        alojamientos = obtener_alojamientos()
        return render_template("inicio.html", alojamientos=alojamientos)

    @app.route("/registro")
    def registro():
        return render_template("registro.html")
