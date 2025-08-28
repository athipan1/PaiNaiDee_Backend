import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

# โหลด environment variables จากไฟล์ .env
# โดยปกติแล้วควรสร้างไฟล์ .env ขึ้นมาเองโดยการ copy จาก .env.example
# และใส่ค่าที่ถูกต้องลงไป
load_dotenv()

def get_engine():
    """
    สร้างและคืนค่า SQLAlchemy engine สำหรับเชื่อมต่อฐานข้อมูล Postgres
    โดยใช้ข้อมูลจาก environment variables
    """
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")
    db_name = os.getenv("DB_NAME")

    # ตรวจสอบว่า environment variables ถูกตั้งค่าครบถ้วนหรือไม่
    if not all([db_user, db_password, db_host, db_port, db_name]):
        raise ValueError("Database environment variables are not fully set. Please check your .env file.")

    # สร้าง Database URL สำหรับ SQLAlchemy
    # รูปแบบ: "postgresql+psycopg2://user:password@host:port/dbname"
    # เพิ่ม `sslmode=require` สำหรับการเชื่อมต่อที่ปลอดภัยไปยัง Supabase
    database_url = (
        f"postgresql+psycopg2://{db_user}:{db_password}@"
        f"{db_host}:{db_port}/{db_name}?sslmode=require"
    )

    # สร้าง engine
    engine = create_engine(database_url)
    return engine

def create_tables(engine, Base):
    """
    สร้างตารางทั้งหมดในฐานข้อมูลที่ engine เชื่อมต่ออยู่
    โดยใช้ metadata จาก Base declarative class
    """
    Base.metadata.create_all(engine)
    print("Tables created successfully.")

if __name__ == '__main__':
    # ส่วนนี้สำหรับการทดสอบการเชื่อมต่อโดยตรง
    try:
        engine = get_engine()
        with engine.connect() as connection:
            print("Database connection successful!")
    except Exception as e:
        print(f"Database connection failed: {e}")
