from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)
from flask import Flask, request, jsonify
import sqlite3


DATABASE = "bookhaven.db"


def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection

def initialize_db():
    connection = get_db_connection()

    # Create feedback table
    connection.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            comment TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create books table
    connection.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL DEFAULT 0
        )
    """)

    connection.commit()
    connection.close()


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
