"""
ACEest Fitness & Gym - Flask Web Application
Version: 3.2.4
"""

from flask import Flask, jsonify, request, render_template_string
import sqlite3
from datetime import datetime

app = Flask(__name__)
DB_NAME = "aceest_fitness.db"

PROGRAMS = {
    "Fat Loss (FL)": {
        "workout": "Mon: Back Squat 5x5 + Core\nTue: EMOM 20min Assault Bike\nWed: Bench Press + 21-15-9\nThu: Deadlift + Box Jumps\nFri: Zone 2 Cardio 30min",
        "diet": "Breakfast: Egg Whites + Oats\nLunch: Grilled Chicken + Brown Rice\nDinner: Fish Curry + Millet Roti\nTarget: ~2000 kcal",
        "calorie_factor": 22
    },
    "Muscle Gain (MG)": {
        "workout": "Mon: Squat 5x5\nTue: Bench 5x5\nWed: Deadlift 4x6\nThu: Front Squat 4x8\nFri: Incline Press 4x10\nSat: Barbell Rows 4x10",
        "diet": "Breakfast: Eggs + PB Oats\nLunch: Chicken Biryani\nDinner: Mutton Curry + Rice\nTarget: ~3200 kcal",
        "calorie_factor": 35
    },
    "Beginner (BG)": {
        "workout": "Full Body Circuit:\n- Air Squats\n- Ring Rows\n- Push-ups\nFocus: Technique & Consistency",
        "diet": "Balanced Tamil Meals\nIdli / Dosa / Rice + Dal\nProtein Target: 120g/day",
        "calorie_factor": 26
    }
}


def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            age INTEGER,
            weight REAL,
            program TEXT,
            calories INTEGER,
            membership_status TEXT DEFAULT 'Active'
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT NOT NULL,
            week TEXT,
            adherence INTEGER
        )
    """)
    conn.commit()
    conn.close()


@app.route("/")
def index():
    return jsonify({
        "app": "ACEest Fitness & Gym",
        "version": "3.2.4",
        "status": "running",
        "endpoints": ["/programs", "/clients", "/clients/<name>", "/progress/<name>"]
    })


@app.route("/health")
def health():
    return jsonify({"status": "healthy", "timestamp": datetime.utcnow().isoformat()})


@app.route("/programs", methods=["GET"])
def get_programs():
    return jsonify(list(PROGRAMS.keys()))


@app.route("/programs/<name>", methods=["GET"])
def get_program(name):
    if name not in PROGRAMS:
        return jsonify({"error": "Program not found"}), 404
    return jsonify(PROGRAMS[name])


@app.route("/clients", methods=["GET"])
def get_clients():
    conn = get_db()
    clients = conn.execute("SELECT * FROM clients").fetchall()
    conn.close()
    return jsonify([dict(c) for c in clients])


@app.route("/clients", methods=["POST"])
def create_client():
    data = request.get_json()
    if not data or not data.get("name") or not data.get("program"):
        return jsonify({"error": "name and program are required"}), 400
    if data["program"] not in PROGRAMS:
        return jsonify({"error": "Invalid program"}), 400

    weight = data.get("weight", 0)
    calories = int(weight * PROGRAMS[data["program"]]["calorie_factor"]) if weight else 0

    try:
        conn = get_db()
        conn.execute(
            "INSERT INTO clients (name, age, weight, program, calories) VALUES (?, ?, ?, ?, ?)",
            (data["name"], data.get("age", 0), weight, data["program"], calories)
        )
        conn.commit()
        conn.close()
        return jsonify({"message": f"Client {data['name']} created", "calories": calories}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Client already exists"}), 409


@app.route("/clients/<name>", methods=["GET"])
def get_client(name):
    conn = get_db()
    client = conn.execute("SELECT * FROM clients WHERE name=?", (name,)).fetchone()
    conn.close()
    if not client:
        return jsonify({"error": "Client not found"}), 404
    return jsonify(dict(client))


@app.route("/clients/<name>", methods=["DELETE"])
def delete_client(name):
    conn = get_db()
    result = conn.execute("DELETE FROM clients WHERE name=?", (name,))
    conn.commit()
    conn.close()
    if result.rowcount == 0:
        return jsonify({"error": "Client not found"}), 404
    return jsonify({"message": f"Client {name} deleted"})


@app.route("/progress/<name>", methods=["POST"])
def save_progress(name):
    data = request.get_json()
    adherence = data.get("adherence", 0)
    if not (0 <= adherence <= 100):
        return jsonify({"error": "Adherence must be 0-100"}), 400

    week = datetime.now().strftime("Week %U - %Y")
    conn = get_db()
    conn.execute(
        "INSERT INTO progress (client_name, week, adherence) VALUES (?, ?, ?)",
        (name, week, adherence)
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Progress saved", "week": week, "adherence": adherence}), 201


@app.route("/calories", methods=["GET"])
def calculate_calories():
    weight = request.args.get("weight", type=float)
    program = request.args.get("program")
    if not weight or not program:
        return jsonify({"error": "weight and program are required"}), 400
    if program not in PROGRAMS:
        return jsonify({"error": "Invalid program"}), 400
    calories = int(weight * PROGRAMS[program]["calorie_factor"])
    return jsonify({"weight": weight, "program": program, "calories": calories})


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=False)