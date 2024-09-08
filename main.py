from flask import Flask, render_template, request, jsonify
from database import init_db, get_db_connection, close_db_connection
import psycopg2
from psycopg2.extras import RealDictCursor
import os

app = Flask(__name__)
app.config['DATABASE_URL'] = os.environ.get('DATABASE_URL')

init_db()

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
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO clubs (name, sport, description) VALUES (%s, %s, %s) RETURNING id",
        (data['name'], data['sport'], data['description'])
    )
    new_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    close_db_connection(conn)
    return jsonify({"id": new_id, "message": "Club added successfully"}), 201

@app.route('/clubs/<int:club_id>', methods=['PUT'])
def update_club(club_id):
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE clubs SET name = %s, sport = %s, description = %s WHERE id = %s",
        (data['name'], data['sport'], data['description'], club_id)
    )
    conn.commit()
    cur.close()
    close_db_connection(conn)
    return jsonify({"message": "Club updated successfully"})

@app.route('/clubs/<int:club_id>', methods=['DELETE'])
def delete_club(club_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM clubs WHERE id = %s", (club_id,))
    conn.commit()
    cur.close()
    close_db_connection(conn)
    return jsonify({"message": "Club deleted successfully"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
