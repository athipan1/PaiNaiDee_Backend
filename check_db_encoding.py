import psycopg2
from src.config import config
import os

def check_encoding():
    conn = None
    try:
        config_name = os.getenv('FLASK_ENV', 'default')
        app_config = config[config_name]
        conn = psycopg2.connect(
            host=app_config.DB_HOST,
            database=app_config.DB_NAME,
            user=app_config.DB_USER,
            password=app_config.DB_PASSWORD,
            port=app_config.DB_PORT
        )
        cur = conn.cursor()
        cur.execute("SHOW server_encoding;")
        encoding = cur.fetchone()
        print(f"Database server encoding: {encoding[0]}")
    except Exception as e:
        print(f"Error checking database encoding: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    check_encoding()
