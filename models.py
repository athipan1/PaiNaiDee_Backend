import datetime
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    Enum,
)
from sqlalchemy.orm import relationship, declarative_base

# สร้าง Base class สำหรับ ORM models ทั้งหมดในโปรเจกต์
# ทุกๆ model จะสืบทอดจาก Base class นี้
Base = declarative_base()

class User(Base):
    """
    Model สำหรับตาราง users
    เก็บข้อมูลผู้ใช้งานในระบบ
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    # 'User' มีความสัมพันธ์แบบ one-to-many กับ 'Project' (1 user เป็นเจ้าของได้หลาย project)
    # back_populates="owner" จะเชื่อมความสัมพันธ์นี้กับ attribute 'owner' ใน Model 'Project'
    projects = relationship("Project", back_populates="owner", cascade="all, delete-orphan")

    # 'User' มีความสัมพันธ์แบบ one-to-many กับ 'Task' (1 user ถูกมอบหมายได้หลาย task)
    # back_populates="assignee" จะเชื่อมความสัมพันธ์นี้กับ attribute 'assignee' ใน Model 'Task'
    tasks = relationship("Task", back_populates="assignee")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"

class Project(Base):
    """
    Model สำหรับตาราง projects
    เก็บข้อมูลโปรเจกต์ต่างๆ
    """
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Foreign Key ที่เชื่อมไปยัง id ของตาราง users
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationships
    # 'Project' มีความสัมพันธ์แบบ many-to-one กับ 'User'
    owner = relationship("User", back_populates="projects")

    # 'Project' มีความสัมพันธ์แบบ one-to-many กับ 'Task'
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.name}')>"

class Task(Base):
    """
    Model สำหรับตาราง tasks
    เก็บข้อมูล task ของแต่ละ project
    """
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)

    # ใช้ Enum เพื่อจำกัดค่าของ status ให้เป็นหนึ่งในตัวเลือกที่กำหนด
    status = Column(Enum("pending", "in_progress", "completed", name="task_status_enum"), default="pending", nullable=False)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    due_date = Column(DateTime, nullable=True)

    # Foreign Keys
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    # 'Task' มีความสัมพันธ์แบบ many-to-one กับ 'Project'
    project = relationship("Project", back_populates="tasks")

    # 'Task' มีความสัมพันธ์แบบ many-to-one กับ 'User'
    assignee = relationship("User", back_populates="tasks")

    def __repr__(self):
        return f"<Task(id={self.id}, title='{self.title}', status='{self.status}')>"
