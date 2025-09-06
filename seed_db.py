import os
from src.app import create_app
from src.models import db, User, Post, VideoPost, Attraction, Like, Comment
from werkzeug.security import generate_password_hash
from datetime import datetime

def seed_database():
    config_name = "testing"
    app = create_app(config_name)
    with app.app_context():
        print("Dropping all tables...")
        db.drop_all()
        print("Creating all tables...")
        db.create_all()
        print("Tables created.")

        print("Seeding database...")

        # Create Users
        users = [
            User(id=1, username="travelbug", email="travelbug@example.com", password=generate_password_hash("password123")),
            User(id=2, username="adventureseeker", email="adventurer@example.com", password=generate_password_hash("password123")),
            User(id=3, username="foodieontour", email="foodie@example.com", password=generate_password_hash("password123")),
        ]
        db.session.bulk_save_objects(users)
        print(f"Seeded {len(users)} users.")

        # Create Attractions
        attractions = [
            Attraction(
                id=1, name="วัดอรุณราชวรารามราชวรมหาวิหาร (วัดแจ้ง)",
                description="วัดอรุณฯ เป็นวัดโบราณที่สร้างขึ้นในสมัยอยุธยา มีชื่อเสียงด้านสถาปัตยกรรมและพระปรางค์ที่สวยงามริมแม่น้ำเจ้าพระยา",
                province="กรุงเทพมหานคร", district="บางกอกใหญ่",
                latitude=13.7437, longitude=100.4889,
                category="วัด", opening_hours="08:00-18:00", entrance_fee="100 บาทสำหรับชาวต่างชาติ",
                contact_phone="02-891-2185", website="https://watarun1.com/",
                main_image_url="https://storage.googleapis.com/painaidee/images/attractions/watarun.jpg"
            ),
            Attraction(
                id=2, name="พระบรมมหาราชวัง",
                description="ศูนย์กลางแห่งประวัติศาสตร์และสถาปัตยกรรมไทย ประกอบด้วยวัดพระแก้วซึ่งประดิษฐานพระแก้วมรกต",
                province="กรุงเทพมหานคร", district="พระนคร",
                latitude=13.7500, longitude=100.4911,
                category="พระราชวัง", opening_hours="08:30-15:30", entrance_fee="500 บาทสำหรับชาวต่างชาติ",
                contact_phone="02-623-5500", website="https://www.royalgrandpalace.th/th/home",
                main_image_url="https://storage.googleapis.com/painaidee/images/attractions/grand_palace.jpg"
            ),
            Attraction(
                id=3, name="วัดพระธาตุดอยสุเทพราชวรวิหาร",
                description="วัดคู่บ้านคู่เมืองเชียงใหม่ สามารถมองเห็นทิวทัศน์เมืองเชียงใหม่ได้จากบนยอดดอย",
                province="เชียงใหม่", district="เมืองเชียงใหม่",
                latitude=18.8050, longitude=98.9216,
                category="วัด", opening_hours="06:00-18:00", entrance_fee="30 บาทสำหรับชาวต่างชาติ",
                contact_phone="053-295-003", website=None,
                main_image_url="https://storage.googleapis.com/painaidee/images/attractions/doisuthep.jpg"
            ),
            Attraction(
                id=4, name="หาดไร่เลย์",
                description="ชายหาดที่สวยงามและมีชื่อเสียงด้านกิจกรรมปีนหน้าผา เข้าถึงได้ทางเรือเท่านั้น",
                province="กระบี่", district="เมืองกระบี่",
                latitude=8.0125, longitude=98.8375,
                category="ชายหาด", opening_hours="ตลอดวัน", entrance_fee="ไม่มี",
                contact_phone=None, website=None,
                main_image_url="https://storage.googleapis.com/painaidee/images/attractions/railay.jpg"
            ),
            Attraction(
                id=5, name="อุทยานประวัติศาสตร์อยุธยา",
                description="ซากปรักหักพังของอดีตราชธานีของไทย ได้รับการขึ้นทะเบียนเป็นมรดกโลกโดย UNESCO",
                province="พระนครศรีอยุธยา", district="พระนครศรีอยุธยา",
                latitude=14.3571, longitude=100.5686,
                category="โบราณสถาน", opening_hours="08:30-18:00", entrance_fee="50 บาทสำหรับชาวต่างชาติ (บางวัด)",
                contact_phone="035-242-286", website="https://www.tourismthailand.org/Attraction/อุทยานประวัติศาสตร์พระนครศรีอยุธยา",
                main_image_url="https://storage.googleapis.com/painaidee/images/attractions/ayutthaya.jpg"
            )
        ]
        db.session.bulk_save_objects(attractions)
        print(f"Seeded {len(attractions)} attractions.")

        # Create Posts
        posts = [
            Post(id=1, user_id=1, content="เพิ่งไปวัดอรุณมา สวยมากเลยครับ ประทับใจสุดๆ #วัดอรุณ #กรุงเทพ", created_at=datetime(2023, 1, 10, 10, 0, 0)),
            Post(id=2, user_id=2, content="พระบรมมหาราชวังคือที่สุดของสถาปัตยกรรมไทยจริงๆ อลังการมาก!", created_at=datetime(2023, 2, 15, 12, 30, 0)),
            Post(id=3, user_id=1, content="ขึ้นดอยสุเทพตอนเช้า อากาศดีมาก เห็นวิวเมืองเชียงใหม่ทั้งหมดเลย", created_at=datetime(2023, 3, 20, 9, 0, 0)),
            Post(id=4, user_id=3, content="หาดไร่เลย์น้ำใส ทรายขาว เหมาะกับการพักผ่อนจริงๆ #กระบี่ #ทะเลใต้", created_at=datetime(2023, 4, 5, 15, 0, 0)),
            Post(id=5, user_id=2, content="หนึ่งวันที่อยุธยา ปั่นจักรยานชมอุทยานประวัติศาสตร์ สนุกและได้ความรู้เยอะเลย", created_at=datetime(2023, 5, 1, 14, 0, 0))
        ]
        db.session.bulk_save_objects(posts)
        print(f"Seeded {len(posts)} posts.")

        # Create VideoPosts
        video_posts = [
            VideoPost(id=1, user_id=3, title="ตะลุยกิน Street Food เยาวราช", video_url="https://storage.googleapis.com/painaidee/videos/bangkok_street_food.mp4", thumbnail_url="https://storage.googleapis.com/painaidee/videos/thumbnails/bangkok_street_food.jpg", created_at=datetime(2023, 1, 12, 18, 0, 0)),
            VideoPost(id=2, user_id=2, title="ปล่อยโคมยี่เป็ง เชียงใหม่", video_url="https://storage.googleapis.com/painaidee/videos/chiangmai_lantern.mp4", thumbnail_url="https://storage.googleapis.com/painaidee/videos/thumbnails/chiangmai_lantern.jpg", created_at=datetime(2022, 11, 8, 20, 0, 0)),
            VideoPost(id=3, user_id=1, title="ทัวร์ 4 เกาะ ทะเลกระบี่", video_url="https://storage.googleapis.com/painaidee/videos/krabi_islands.mp4", thumbnail_url="https://storage.googleapis.com/painaidee/videos/thumbnails/krabi_islands.jpg", created_at=datetime(2023, 4, 7, 11, 0, 0))
        ]
        db.session.bulk_save_objects(video_posts)
        print(f"Seeded {len(video_posts)} video posts.")

        # Create some engagement data
        likes = [
            Like(user_id=1, post_id=2),
            Like(user_id=2, post_id=1),
            Like(user_id=3, post_id=1),
            Like(user_id=1, video_post_id=2),
            Like(user_id=2, video_post_id=3),
        ]
        db.session.bulk_save_objects(likes)
        print(f"Seeded {len(likes)} likes.")

        comments = [
            Comment(user_id=2, post_id=1, content="สวยจริงๆ ครับ!"),
            Comment(user_id=1, post_id=2, content="ต้องไปให้ได้เลย"),
            Comment(user_id=3, video_post_id=1, content="น่ากินมากกก"),
        ]
        db.session.bulk_save_objects(comments)
        print(f"Seeded {len(comments)} comments.")

        db.session.commit()
        print("Database seeded successfully.")

if __name__ == "__main__":
    seed_database()
