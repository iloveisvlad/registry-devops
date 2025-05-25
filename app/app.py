from flask import Flask, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime

app = Flask(__name__)

DB_PARAMS = {
    'dbname': os.environ.get('POSTGRES_DB', 'registry'),
    'user': os.environ.get('POSTGRES_USER', 'postgres'),
    'password': os.environ.get('POSTGRES_PASSWORD', 'postgres'),
    'host': os.environ.get('POSTGRES_HOST', 'localhost'),
    'port': os.environ.get('POSTGRES_PORT', 5432)
}


def get_db_connection():
    return psycopg2.connect(**DB_PARAMS, cursor_factory=RealDictCursor)


def serialize_appointment(row):
    import datetime as dt
    row['date'] = row['date'].strftime(
        "%Y-%m-%d") if isinstance(row['date'], dt.date) else row['date']
    row['time'] = row['time'].strftime("%H:%M:%S") if isinstance(
        row['time'], dt.time) else row['time']
    return row


@app.route("/patients", methods=["GET", "POST"])
def patients():
    conn = get_db_connection()
    cur = conn.cursor()
    if request.method == "GET":
        cur.execute("SELECT * FROM patient")
        patients = cur.fetchall()
        conn.close()
        return jsonify(patients)

    if request.method == "POST":
        data = request.json
        cur.execute(
            "INSERT INTO patient (name, address, phone) VALUES (%s, %s, %s) RETURNING *",
            (data["name"], data["address"], data["phone"])
        )
        patient = cur.fetchone()
        conn.commit()
        conn.close()
        return jsonify(patient), 201


@app.route("/patients/<int:id>", methods=["GET", "PUT", "DELETE"])
def patient(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM patient WHERE id = %s", (id,))
    patient = cur.fetchone()

    if request.method == "GET":
        conn.close()
        return jsonify(patient)

    if request.method == "PUT":
        data = request.json
        cur.execute(
            "UPDATE patient SET name = %s, address = %s, phone = %s WHERE id = %s RETURNING *",
            (data["name"], data["address"], data["phone"], id)
        )
        updated = cur.fetchone()
        conn.commit()
        conn.close()
        return jsonify(updated)

    if request.method == "DELETE":
        cur.execute("DELETE FROM patient WHERE id = %s", (id,))
        conn.commit()
        conn.close()
        return '', 204


@app.route("/doctors", methods=["GET", "POST"])
def doctors():
    conn = get_db_connection()
    cur = conn.cursor()
    if request.method == "GET":
        cur.execute("SELECT * FROM doctor")
        doctors = cur.fetchall()
        conn.close()
        return jsonify(doctors)

    if request.method == "POST":
        data = request.json
        cur.execute(
            "INSERT INTO doctor (name) VALUES (%s) RETURNING *",
            (data["name"],)
        )
        doctor = cur.fetchone()
        conn.commit()
        conn.close()
        return jsonify(doctor), 201


@app.route("/specializations", methods=["GET", "POST"])
def specializations():
    conn = get_db_connection()
    cur = conn.cursor()
    if request.method == "GET":
        cur.execute("SELECT * FROM specialization")
        specs = cur.fetchall()
        conn.close()
        return jsonify(specs)

    if request.method == "POST":
        data = request.json
        cur.execute(
            "INSERT INTO specialization (name) VALUES (%s) RETURNING *",
            (data["name"],)
        )
        spec = cur.fetchone()
        conn.commit()
        conn.close()
        return jsonify(spec), 201


@app.route("/doctor_specializations", methods=["GET", "POST"])
def doctor_specializations():
    conn = get_db_connection()
    cur = conn.cursor()
    if request.method == "GET":
        cur.execute("SELECT * FROM doctor_specialization")
        result = cur.fetchall()
        conn.close()
        return jsonify(result)

    if request.method == "POST":
        data = request.json
        cur.execute(
            "INSERT INTO doctor_specialization (doctor_id, specialization_id) VALUES (%s, %s) RETURNING *",
            (data["doctor_id"], data["specialization_id"])
        )
        link = cur.fetchone()
        conn.commit()
        conn.close()
        return jsonify(link), 201


@app.route("/doctor_specializations/<int:id>", methods=["DELETE"])
def delete_doctor_specialization(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM doctor_specialization WHERE id = %s", (id,))
    conn.commit()
    conn.close()
    return '', 204


@app.route("/rooms", methods=["GET", "POST"])
def rooms():
    conn = get_db_connection()
    cur = conn.cursor()
    if request.method == "GET":
        cur.execute("SELECT * FROM room")
        rooms = cur.fetchall()
        conn.close()
        return jsonify(rooms)

    if request.method == "POST":
        data = request.json
        cur.execute(
            "INSERT INTO room (name) VALUES (%s) RETURNING *",
            (data["name"],)
        )
        room = cur.fetchone()
        conn.commit()
        conn.close()
        return jsonify(room), 201


@app.route("/appointments", methods=["GET", "POST"])
def appointments():
    conn = get_db_connection()
    cur = conn.cursor()
    if request.method == "GET":
        cur.execute("SELECT * FROM appointment")
        appointments = cur.fetchall()
        conn.close()
        return jsonify([serialize_appointment(row) for row in appointments])

    if request.method == "POST":
        data = request.json
        cur.execute(
            "INSERT INTO appointment (patient_id, doctor_id, time, date, room_id, status) VALUES (%s, %s, %s, %s, %s, %s) RETURNING *",
            (
                data["patient_id"],
                data["doctor_id"],
                data["time"],
                data["date"],
                data["room_id"],
                data["status"]
            )
        )
        appointment = cur.fetchone()
        conn.commit()
        conn.close()
        return jsonify(serialize_appointment(appointment)), 201


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
