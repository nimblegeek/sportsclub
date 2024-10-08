import psycopg2
from psycopg2.extras import RealDictCursor
import os

def get_db_connection():
    conn = psycopg2.connect(
        host=os.environ.get('PGHOST'),
        database=os.environ.get('PGDATABASE'),
        user=os.environ.get('PGUSER'),
        password=os.environ.get('PGPASSWORD'),
        port=os.environ.get('PGPORT')
    )
    return conn

def close_db_connection(conn):
    conn.close()

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS clubs (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            sport VARCHAR(50) NOT NULL,
            description TEXT,
            organizational_number VARCHAR(20)
        )
    ''')
    conn.commit()
    cur.close()
    close_db_connection(conn)

def add_organizational_number_column():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        ALTER TABLE clubs
        ADD COLUMN IF NOT EXISTS organizational_number VARCHAR(20)
    ''')
    conn.commit()
    cur.close()
    close_db_connection(conn)

# Call this function to add the new column
add_organizational_number_column()
