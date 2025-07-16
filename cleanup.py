import psycopg2
from src.config import config
import os
import json

def cleanup_database():
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

        # Delete records with invalid characters
        cur.execute("DELETE FROM attractions WHERE name LIKE '????%' OR province LIKE '????%' OR description LIKE '????%';")
        deleted_rows = cur.rowcount
        print(f"Deleted {deleted_rows} rows with invalid characters.")

        # Delete records with unparsable image_urls
        cur.execute("SELECT id, image_urls FROM attractions;")
        rows = cur.fetchall()
        deleted_count = 0
        for row in rows:
            try:
                if isinstance(row[1], str):
                    json.loads(row[1])
            except (json.JSONDecodeError, TypeError):
                cur.execute("DELETE FROM attractions WHERE id = %s;", (row[0],))
                deleted_count += 1

        print(f"Deleted {deleted_count} rows with unparsable image_urls.")

        conn.commit()

    except Exception as e:
        print(f"Error during database cleanup: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    cleanup_database()
