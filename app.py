
from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

DATABASE = "bookhaven.db"


def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


@app.route("/")
def home():
    return "Book Haven backend is running!"


@app.route("/api/feedback", methods=["POST"])
def add_feedback():
    data = request.get_json(silent=True) or {}

    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    comment = data.get("comment", "").strip()

    if not name or not email or not comment:
        return jsonify({"error": "All fields are required"}), 400

    connection = get_db_connection()

    connection.execute(
        """
        INSERT INTO feedback (name, email, comment)
        VALUES (?, ?, ?)
        """,
        (name, email, comment)
    )

    connection.commit()
    connection.close()

    return jsonify({"message": "Feedback saved successfully!"}), 201


if __name__ == "__main__":
    app.run(debug=True)
