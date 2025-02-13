from flask import Flask, render_template, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pycountry
import os
import csv

app = Flask(__name__)

# Configuración de la base de datos (SQLite)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "datos_turismo.db")
db = SQLAlchemy(app)

# Definición del modelo de datos
class Registro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hora = db.Column(db.String(8))
    fecha = db.Column(db.String(10))
    nacionalidad = db.Column(db.String(100))
    motivo_visita = db.Column(db.String(100))
    descubrimiento = db.Column(db.String(255))
    viaje = db.Column(db.String(50))
    transporte = db.Column(db.String(50))
    comuna = db.Column(db.String(100))

# Crear la tabla si no existe
with app.app_context():
    db.create_all()

def obtener_nacionalidades():
    """Obtiene la lista de nombres de países desde pycountry."""
    return [pais.name for pais in pycountry.countries]

@app.route("/", methods=["GET", "POST"])
def index():
    nacionalidades = obtener_nacionalidades()
    comunas_chile = ["Algarrobo", "Alhué", "Alto Biobío", "Alto del Carmen", "Alto Hospicio", "Ancud"]  # Lista de comunas (ejemplo)

    if request.method == "POST":
        hora_actual = datetime.now().strftime("%H:%M:%S")
        fecha_actual = datetime.now().strftime("%Y-%m-%d")
        nacionalidad = request.form.get("nacionalidad")
        motivo_visita = request.form.get("motivo_visita")
        descubrimiento = request.form.get("descubrimiento")
        viaje = request.form.get("viaje")
        transporte = request.form.get("transporte")
        comuna = request.form.get("comuna") if nacionalidad == "Chile" else ""

        registro = Registro(  # Crea un nuevo registro
            hora=hora_actual,
            fecha=fecha_actual,
            nacionalidad=nacionalidad,
            motivo_visita=motivo_visita,
            descubrimiento=descubrimiento,
            viaje=viaje,
            transporte=transporte,
            comuna=comuna
        )

        try:
            db.session.add(registro)  # Guarda el registro en la base de datos
            db.session.commit()
            return jsonify({"message": "Datos guardados correctamente."})
        except Exception as e:
            db.session.rollback()  # Revierte los cambios en caso de error
            return jsonify({"error": str(e)})

    return render_template("index.html", nacionalidades=nacionalidades, comunas_chile=comunas_chile)

@app.route("/generar_csv")
def generar_csv():
    try:
        registros = Registro.query.all()
        nombre_archivo = "datos_turismo.csv"
        # Generar el archivo CSV en memoria
        with open("datos_turismo.csv", "w", newline="", encoding="utf-8") as archivo:
            escritor = csv.writer(archivo)
            escritor.writerow(["Hora", "Fecha", "Nacionalidad", "Motivo Principal de Visita",
                             "Cómo se Enteró de Panguipulli", "Con Quién Viajó",
                             "Medio de Transporte Principal", "Comuna de Residencia (Chile)"])
            for registro in registros:
                escritor.writerow([registro.hora, registro.fecha, registro.nacionalidad,
                                     registro.motivo_visita, registro.descubrimiento, registro.viaje,
                                     registro.transporte, registro.comuna])

        # Enviar el archivo CSV como respuesta descargable
        return send_file(
            nombre_archivo,
            mimetype="text/csv",
            as_attachment=True,
            download_name=nombre_archivo
        )
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(debug=True)
