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
            User(id=4, username="beachlover", email="beachlover@example.com", password=generate_password_hash("password123")),
            User(id=5, username="historygeek", email="historygeek@example.com", password=generate_password_hash("password123")),
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
                id=5, name="อุทยานประวัติศาสตร์สุโขทัย",
                description="อาณาจักรแรกของชนชาติไทยที่ได้รับการขึ้นทะเบียนเป็นมรดกโลก มีความสวยงามของโบราณสถานที่เป็นเอกลักษณ์",
                province="สุโขทัย", district="เมืองเก่า",
                latitude=17.0173, longitude=99.7039,
                category="โบราณสถาน", opening_hours="08:30-18:30", entrance_fee="100 บาทสำหรับชาวต่างชาติ",
                contact_phone="055-697-241", website="https://www.sukhothai.go.th/tour/tour_01.htm",
                main_image_url="https://storage.googleapis.com/painaidee/images/attractions/sukhothai.jpg"
            ),
            Attraction(
                id=6, name="ตลาดน้ำดำเนินสะดวก",
                description="ตลาดน้ำที่เก่าแก่ที่สุดของไทย เต็มไปด้วยเรือขายอาหารและของที่ระลึก เป็นที่นิยมของนักท่องเที่ยวต่างชาติ",
                province="ราชบุรี", district="ดำเนินสะดวก",
                latitude=13.5186, longitude=99.9590,
                category="ตลาด", opening_hours="07:00-12:00", entrance_fee="ไม่มี",
                contact_phone=None, website=None,
                main_image_url="https://storage.googleapis.com/painaidee/images/attractions/damnoen_saduak.jpg"
            ),
            Attraction(
                id=7, name="อุทยานแห่งชาติเขาใหญ่",
                description="อุทยานแห่งชาติแห่งแรกของประเทศไทย เป็นมรดกโลกทางธรรมชาติ มีสัตว์ป่าและน้ำตกที่สวยงามมากมาย",
                province="นครราชสีมา", district="ปากช่อง",
                latitude=14.4388, longitude=101.3759,
                category="อุทยานแห่งชาติ", opening_hours="06:00-18:00", entrance_fee="400 บาทสำหรับชาวต่างชาติ",
                contact_phone="086-092-6529", website="https://khaoyainationalpark.com/",
                main_image_url="https://storage.googleapis.com/painaidee/images/attractions/khao_yai.jpg"
            )
        ]
        db.session.bulk_save_objects(attractions)
        print(f"Seeded {len(attractions)} attractions.")

        # Create Posts
        posts = [
            Post(id=1, user_id=1, title="ประทับใจวัดอรุณ", content="เพิ่งไปวัดอรุณมา สวยมากเลยครับ ประทับใจสุดๆ #วัดอรุณ #กรุงเทพ", created_at=datetime(2023, 1, 10, 10, 0, 0)),
            Post(id=2, user_id=2, title="เที่ยววังหลวง", content="พระบรมมหาราชวังคือที่สุดของสถาปัตยกรรมไทยจริงๆ อลังการมาก!", created_at=datetime(2023, 2, 15, 12, 30, 0)),
            Post(id=3, user_id=1, title="ดอยสุเทพตอนเช้า", content="ขึ้นดอยสุเทพตอนเช้า อากาศดีมาก เห็นวิวเมืองเชียงใหม่ทั้งหมดเลย", created_at=datetime(2023, 3, 20, 9, 0, 0)),
            Post(id=4, user_id=4, title="พักผ่อนที่ไร่เลย์", content="หาดไร่เลย์น้ำใส ทรายขาว เหมาะกับการพักผ่อนจริงๆ #กระบี่ #ทะเลใต้", created_at=datetime(2023, 4, 5, 15, 0, 0)),
            Post(id=5, user_id=5, title="ปั่นจักรยานที่สุโขทัย", content="หนึ่งวันที่สุโขทัย ปั่นจักรยานชมอุทยานประวัติศาสตร์ สนุกและได้ความรู้เยอะเลย", created_at=datetime(2023, 5, 1, 14, 0, 0)),
            Post(id=6, user_id=3, title="ของกินตลาดน้ำ", content="ของกินที่ตลาดน้ำดำเนินสะดวกอร่อยทุกอย่างเลย โดยเฉพาะก๋วยเตี๋ยวเรือ", created_at=datetime(2023, 6, 10, 11, 0, 0)),
            Post(id=7, user_id=2, title="เจอช้างที่เขาใหญ่", content="ไปส่องสัตว์ที่เขาใหญ่มา โชคดีมากได้เจอโขลงช้างด้วย!", created_at=datetime(2023, 7, 22, 16, 30, 0)),
            Post(id=8, user_id=1, title="ไหว้พระที่วัดแจ้งอีกรอบ", content="กลับมาวัดอรุณอีกครั้งตอนกลางคืน เปิดไฟสวยงามไปอีกแบบ", created_at=datetime(2023, 8, 1, 19, 0, 0)),
            Post(id=9, user_id=4, title="ปีนผาที่กระบี่", content="ลองปีนผาครั้งแรกที่อ่าวไร่เลย์ สนุกและท้าทายมาก!", created_at=datetime(2023, 9, 5, 14, 0, 0)),
            Post(id=10, user_id=5, title="มรดกโลกอยุธยา", content="อุทยานประวัติศาสตร์อยุธยา (คนละที่กับสุโขทัยนะ) ก็สวยไม่แพ้กันเลย", created_at=datetime(2023, 10, 15, 13, 0, 0)),
        ]
        db.session.bulk_save_objects(posts)
        print(f"Seeded {len(posts)} posts.")

        # Create VideoPosts
        video_posts = [
            VideoPost(id=1, user_id=3, title="ตะลุยกิน Street Food เยาวราช", video_url="https://storage.googleapis.com/painaidee/videos/bangkok_street_food.mp4", thumbnail_url="https://storage.googleapis.com/painaidee/videos/thumbnails/bangkok_street_food.jpg", created_at=datetime(2023, 1, 12, 18, 0, 0)),
            VideoPost(id=2, user_id=2, title="ปล่อยโคมยี่เป็ง เชียงใหม่", video_url="https://storage.googleapis.com/painaidee/videos/chiangmai_lantern.mp4", thumbnail_url="https://storage.googleapis.com/painaidee/videos/thumbnails/chiangmai_lantern.jpg", created_at=datetime(2022, 11, 8, 20, 0, 0)),
            VideoPost(id=3, user_id=1, title="ทัวร์ 4 เกาะ ทะเลกระบี่", video_url="https://storage.googleapis.com/painaidee/videos/krabi_islands.mp4", thumbnail_url="https://storage.googleapis.com/painaidee/videos/thumbnails/krabi_islands.jpg", created_at=datetime(2023, 4, 7, 11, 0, 0)),
            VideoPost(id=4, user_id=4, title="ดำน้ำดูปะการังที่พีพี", video_url="https://storage.googleapis.com/painaidee/videos/phiphi_diving.mp4", thumbnail_url="https://storage.googleapis.com/painaidee/videos/thumbnails/phiphi_diving.jpg", created_at=datetime(2023, 5, 20, 14, 0, 0)),
            VideoPost(id=5, user_id=5, title="เดินชมเมืองเก่าสุโขทัย", video_url="https://storage.googleapis.com/painaidee/videos/sukhothai_tour.mp4", thumbnail_url="https://storage.googleapis.com/painaidee/videos/thumbnails/sukhothai_tour.jpg", created_at=datetime(2023, 6, 25, 10, 30, 0)),
            VideoPost(id=6, user_id=2, title="ผจญภัยในถ้ำที่เขาใหญ่", video_url="https://storage.googleapis.com/painaidee/videos/khaoyai_caving.mp4", thumbnail_url="https://storage.googleapis.com/painaidee/videos/thumbnails/khaoyai_caving.jpg", created_at=datetime(2023, 8, 30, 12, 0, 0)),
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
