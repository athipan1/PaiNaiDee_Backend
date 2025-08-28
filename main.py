from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

# นำเข้า engine,ฟังก์ชันสร้างตาราง, และ Base declarative class
from database import get_engine, create_tables
from models import Base, User, Project, Task

def main():
    """
    ฟังก์ชันหลักสำหรับสาธิตการทำงาน
    1. สร้างตาราง
    2. เพิ่มข้อมูลตัวอย่าง
    3. ดึงข้อมูลและแสดงผล
    """
    # 1. เชื่อมต่อฐานข้อมูลและสร้างตาราง
    # -------------------------------------
    try:
        engine = get_engine()
        # สร้างตารางทั้งหมด (ถ้ายังไม่มี)
        # SQLAlchemy จะตรวจสอบก่อนว่าตารางมีอยู่แล้วหรือไม่
        create_tables(engine, Base)
    except Exception as e:
        print(f"Failed to connect to the database or create tables: {e}")
        return

    # 2. เพิ่มข้อมูลตัวอย่าง
    # -------------------------------------
    # สร้าง Session class สำหรับการโต้ตอบกับฐานข้อมูล
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # สร้าง instance ของ session
    db_session = SessionLocal()

    try:
        print("\n--- Adding sample data ---")

        # ตรวจสอบว่ามีข้อมูลอยู่แล้วหรือไม่ เพื่อไม่ให้เพิ่มข้อมูลซ้ำซ้อน
        if db_session.query(User).first():
            print("Sample data already exists. Skipping data insertion.")
        else:
            # สร้าง User 2 คน
            user1 = User(username="jules_dev", email="jules.dev@example.com")
            user2 = User(username="jane_doe", email="jane.doe@example.com")

            # สร้าง Project โดยให้ user1 เป็นเจ้าของ
            project1 = Project(
                name="SQLAlchemy Integration",
                description="A project to demonstrate Supabase connection.",
                owner=user1
            )

            # สร้าง Task 3 อันใน project1
            task1 = Task(
                title="Setup database connection",
                description="Write the code for database.py",
                project=project1,
                assignee=user1,
                status="completed"
            )
            task2 = Task(
                title="Create ORM Models",
                description="Define User, Project, and Task models.",
                project=project1,
                assignee=user1,
                status="in_progress"
            )
            task3 = Task(
                title="Write main application",
                description="Create main.py to test everything.",
                project=project1,
                assignee=user2
            )

            # เพิ่ม object ทั้งหมดลงใน session
            db_session.add_all([user1, user2, project1, task1, task2, task3])

            # Commit (บันทึก) การเปลี่ยนแปลงลงฐานข้อมูล
            db_session.commit()
            print("Sample data added successfully.")

    except Exception as e:
        print(f"An error occurred while adding data: {e}")
        db_session.rollback() # ย้อนกลับการเปลี่ยนแปลงถ้ามีปัญหา
    finally:
        # 3. ดึงข้อมูลและแสดงผล
        # -------------------------------------
        print("\n--- Querying data ---")

        # ดึงข้อมูล Users ทั้งหมด
        all_users = db_session.query(User).all()
        print("\n[All Users]")
        for user in all_users:
            print(f"- {user}")

        # ดึงข้อมูล Projects ทั้งหมด พร้อมแสดงชื่อเจ้าของ
        all_projects = db_session.query(Project).all()
        print("\n[All Projects]")
        for project in all_projects:
            print(f"- Project: '{project.name}', Owner: {project.owner.username}")

        # ดึงข้อมูล Tasks ทั้งหมด พร้อมแสดงชื่อโปรเจกต์และผู้รับผิดชอบ
        all_tasks = db_session.query(Task).all()
        print("\n[All Tasks]")
        for task in all_tasks:
            assignee_name = task.assignee.username if task.assignee else "N/A"
            print(f"- Task: '{task.title}', Project: '{task.project.name}', Assignee: {assignee_name}, Status: {task.status}")

        # ตัวอย่างการ Query ที่ซับซ้อน: หา user 'jules_dev' และแสดงโปรเจกต์และ task ของเขา
        print("\n[Jules's Projects and Tasks]")
        jules = db_session.query(User).filter_by(username="jules_dev").first()
        if jules:
            print(f"User: {jules.username}")
            for proj in jules.projects:
                print(f"  - Owns Project: {proj.name}")
                for t in proj.tasks:
                     print(f"    - Task: {t.title} (Assigned to: {t.assignee.username})")

        # ปิด session เมื่อใช้งานเสร็จ
        db_session.close()
        print("\nDatabase session closed.")

if __name__ == "__main__":
    main()
