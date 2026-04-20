from flask import send_file
from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime
import csv

app = Flask(__name__)

DB_NAME = "database.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        rating INTEGER,
        comments TEXT,
        date_submitted TEXT
    )
    """)

    conn.commit()
    conn.close()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/submit-feedback", methods=["POST"])
def submit_feedback():
    name = request.form["name"]
    email = request.form["email"]
    rating = request.form["rating"]
    comments = request.form["comments"]

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO feedback (name, email, rating, comments, date_submitted)
    VALUES (?, ?, ?, ?, ?)
    """, (name, email, rating, comments, datetime.now()))

    conn.commit()
    conn.close()

    return redirect("/admin-dashboard")


@app.route("/admin-dashboard")
def admin_dashboard():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM feedback")
    data = cursor.fetchall()

    total = len(data)
    avg_rating = round(sum([row[3] for row in data]) / total, 2) if total > 0 else 0

    conn.close()

    return render_template("admin.html", data=data, total=total, avg=avg_rating)


@app.route("/export")
def export_csv():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM feedback")
    data = cursor.fetchall()

    file_path = "feedback.csv"

    with open(file_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Name", "Email", "Rating", "Comments", "Date"])
        writer.writerows(data)

    conn.close()

    return send_file(file_path, as_attachment=True)


if __name__ == "__main__":
    init_db()
    app.run(debug=True)