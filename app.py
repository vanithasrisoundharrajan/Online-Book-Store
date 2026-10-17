
import math
from decimal import Decimal, InvalidOperation

from flask import Flask, jsonify, request, send_from_directory
from db import get_db_connection

app = Flask(__name__, static_folder="static", static_url_path="")


# Create the books table in MySQL
def initialize_database():
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id INT PRIMARY KEY AUTO_INCREMENT,
                title VARCHAR(150) NOT NULL,
                author VARCHAR(100) NOT NULL,
                price DECIMAL(10, 2) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        connection.commit()
        print("Books table is ready.")
    finally:
        cursor.close()
        connection.close()


# Validate book details received from the frontend
def validate_book(data):
    if not isinstance(data, dict):
        return None, "Send book details as JSON."

    title = data.get("title")
    author = data.get("author")
    price = data.get("price")

    if not isinstance(title, str) or not title.strip():
        return None, "Title is required."

    if not isinstance(author, str) or not author.strip():
        return None, "Author is required."

    if len(title.strip()) > 150 or len(author.strip()) > 100:
        return None, "Title or author is too long."

    try:
        price = Decimal(str(price))

        if (
            not price.is_finite()
            or price < 0
            or price > Decimal("99999999.99")
        ):
            return None, "Enter a valid non-negative price."

        price = price.quantize(Decimal("0.01"))

    except (InvalidOperation, ValueError, TypeError):
        return None, "Enter a valid price."

    return {
        "title": title.strip(),
        "author": author.strip(),
        "price": price
    }, None


# Convert MySQL records into JSON-friendly dictionaries
def format_book(row):
    return {
        "id": row["id"],
        "title": row["title"],
        "author": row["author"],
        "price": float(row["price"])
    }


# Serve your existing frontend
@app.route("/")
def home():
    return send_from_directory(app.static_folder, "index.html")


# READ: Get all books
@app.route("/api/books", methods=["GET"])
def get_books():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT id, title, author, price
            FROM books
            ORDER BY id DESC
        """)
        return jsonify([format_book(row) for row in cursor.fetchall()])
    finally:
        cursor.close()
        connection.close()


# READ: Get one book
@app.route("/api/books/<int:book_id>", methods=["GET"])
def get_book(book_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT id, title, author, price
            FROM books
            WHERE id = %s
        """, (book_id,))

        row = cursor.fetchone()

        if row is None:
            return jsonify({"error": "Book not found"}), 404

        return jsonify(format_book(row))
    finally:
        cursor.close()
        connection.close()


# CREATE: Add a book
@app.route("/api/books", methods=["POST"])
def create_book():
    data, error = validate_book(request.get_json(silent=True))

    if error:
        return jsonify({"error": error}), 400

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            INSERT INTO books (title, author, price)
            VALUES (%s, %s, %s)
        """, (data["title"], data["author"], data["price"]))

        connection.commit()
        book_id = cursor.lastrowid

        return jsonify({
            "message": "Book added successfully",
            "id": book_id
        }), 201
    finally:
        cursor.close()
        connection.close()


# UPDATE: Edit a book
@app.route("/api/books/<int:book_id>", methods=["PUT"])
def update_book(book_id):
    data, error = validate_book(request.get_json(silent=True))

    if error:
        return jsonify({"error": error}), 400

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            UPDATE books
            SET title = %s, author = %s, price = %s
            WHERE id = %s
        """, (
            data["title"],
            data["author"],
            data["price"],
            book_id
        ))

        connection.commit()

        if cursor.rowcount == 0:
            cursor.execute(
                "SELECT id FROM books WHERE id = %s",
                (book_id,)
            )

            if cursor.fetchone() is None:
                return jsonify({"error": "Book not found"}), 404

        return jsonify({"message": "Book updated successfully"})
    finally:
        cursor.close()
        connection.close()


# DELETE: Remove a book
@app.route("/api/books/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            "DELETE FROM books WHERE id = %s",
            (book_id,)
        )
        connection.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Book not found"}), 404

        return jsonify({"message": "Book deleted successfully"})
    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    initialize_database()
    app.run(host="0.0.0.0", port=5000, debug=True)
