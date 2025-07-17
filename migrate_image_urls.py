import os
import psycopg2
import json
from src.config import config

def migrate():
    config_name = os.getenv('FLASK_ENV', 'default')
    db_config = config[config_name]

    conn = None
    try:
        conn = psycopg2.connect(
            host=db_config.DB_HOST,
            database=db_config.DB_NAME,
            user=db_config.DB_USER,
            password=db_config.DB_PASSWORD,
            port=db_config.DB_PORT
        )
        cur = conn.cursor()

        # 1. Add a new temporary column with the ARRAY type
        cur.execute("ALTER TABLE attractions ADD COLUMN image_urls_new TEXT[]")

        # 2. Fetch all rows with the old image_urls
        cur.execute("SELECT id, image_urls FROM attractions WHERE image_urls IS NOT NULL")
        rows = cur.fetchall()

        # 3. Update the new column with data from the old column
        for row in rows:
            try:
                image_urls_list = json.loads(row[1])
                if isinstance(image_urls_list, list):
                    cur.execute("UPDATE attractions SET image_urls_new = %s WHERE id = %s", (image_urls_list, row[0]))
            except (json.JSONDecodeError, TypeError):
                continue

        # 4. Drop the old column
        cur.execute("ALTER TABLE attractions DROP COLUMN image_urls")

        # 5. Rename the new column to the original name
        cur.execute("ALTER TABLE attractions RENAME COLUMN image_urls_new TO image_urls")

        conn.commit()
        print("Migration successful: 'image_urls' column has been converted to TEXT[]")

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"An error occurred during migration: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    migrate()
