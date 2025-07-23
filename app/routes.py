from flask import render_template
from app.models import obtener_alojamientos

def init_routes(app):
    @app.route("/")
    def inicio():
        alojamientos = obtener_alojamientos()
        return render_template("inicio.html", alojamientos=alojamientos)