from flask import Flask, render_template, request, jsonify
from database import init_db, get_db_connection, close_db_connection, add_organizational_number_column
import psycopg2
from psycopg2.extras import RealDictCursor
import os

app = Flask(__name__)
app.config['DATABASE_URL'] = os.environ.get('DATABASE_URL')

init_db()
add_organizational_number_column()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/clubs', methods=['GET'])
def get_clubs():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM clubs")
    clubs = cur.fetchall()
    cur.close()
    close_db_connection(conn)
    return jsonify(clubs)

@app.route('/clubs', methods=['POST'])
def add_club():
    data = request.json
    if not data.get('organizational_number'):
        return jsonify({"error": "Organizational number is required"}), 400
    
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO clubs (name, sport, description, organizational_number) VALUES (%s, %s, %s, %s) RETURNING id",
            (data['name'], data['sport'], data['description'], data['organizational_number'])
        )
        new_id = cur.fetchone()[0]
        conn.commit()
        return jsonify({"id": new_id, "message": "Club added successfully"}), 201
    except psycopg2.Error as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()
        close_db_connection(conn)

@app.route('/clubs/<int:club_id>', methods=['PUT'])
def update_club(club_id):
    data = request.json
    if not data.get('organizational_number'):
        return jsonify({"error": "Organizational number is required"}), 400
    
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "UPDATE clubs SET name = %s, sport = %s, description = %s, organizational_number = %s WHERE id = %s",
            (data['name'], data['sport'], data['description'], data['organizational_number'], club_id)
        )
        if cur.rowcount == 0:
            return jsonify({"error": "Club not found"}), 404
        conn.commit()
        return jsonify({"message": "Club updated successfully"})
    except psycopg2.Error as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()
        close_db_connection(conn)

@app.route('/clubs/<int:club_id>', methods=['DELETE'])
def delete_club(club_id):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM clubs WHERE id = %s", (club_id,))
        if cur.rowcount == 0:
            return jsonify({"error": "Club not found"}), 404
        conn.commit()
        return jsonify({"message": "Club deleted successfully"})
    except psycopg2.Error as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()
        close_db_connection(conn)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
