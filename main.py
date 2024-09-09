from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from database import init_db, get_db_connection, close_db_connection, add_organizational_number_column
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
from urllib.parse import quote_plus, urlencode
import json  # Add this import

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['DATABASE_URL'] = os.environ.get('DATABASE_URL')

oauth = OAuth(app)

auth0 = oauth.register(
    'auth0',
    client_id=os.environ.get("AUTH0_CLIENT_ID"),
    client_secret=os.environ.get("AUTH0_CLIENT_SECRET"),
    api_base_url=f"https://{os.environ.get('AUTH0_DOMAIN')}",
    access_token_url=f"https://{os.environ.get('AUTH0_DOMAIN')}/oauth/token",
    authorize_url=f"https://{os.environ.get('AUTH0_DOMAIN')}/authorize",
    client_kwargs={
        'scope': 'openid profile email',
    },
)

init_db()
add_organizational_number_column()

@app.route('/')
def index():
    return render_template('index.html', session=session.get('user'), pretty=json.dumps(session.get('user'), indent=4))

@app.route('/login')
def login():
    return auth0.authorize_redirect(redirect_uri=url_for('callback', _external=True))

@app.route('/callback')
def callback():
    auth0.authorize_access_token()
    resp = auth0.get('userinfo')
    userinfo = resp.json()
    session['jwt_payload'] = userinfo
    session['user'] = {
        'user_id': userinfo['sub'],
        'name': userinfo.get('name', ''),
        'picture': userinfo.get('picture', '')
    }
    return redirect('/')

@app.route('/logout')
def logout():
    session.clear()
    params = {'returnTo': url_for('index', _external=True), 'client_id': os.environ.get("AUTH0_CLIENT_ID")}
    return redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))

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
    if 'user' not in session:
        return jsonify({"error": "Authentication required"}), 401
    
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
    if 'user' not in session:
        return jsonify({"error": "Authentication required"}), 401
    
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
    if 'user' not in session:
        return jsonify({"error": "Authentication required"}), 401
    
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
