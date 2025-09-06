import os
from src.app import create_app
from src.models import db, User, Post, VideoPost, Attraction, Like, Comment
from werkzeug.security import generate_password_hash

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
            User(id=1, username="testuser1", email="test1@example.com", password=generate_password_hash("password")),
            User(id=2, username="testuser2", email="test2@example.com", password=generate_password_hash("password")),
        ]
        db.session.bulk_save_objects(users)
        print(f"Seeded {len(users)} users.")

        # Create Attractions
        attractions = [
            Attraction(id=1, name="Eiffel Tower", province="Paris", main_image_url="https://example.com/eiffel.jpg"),
            Attraction(id=2, name="Statue of Liberty", province="New York", main_image_url="https://example.com/liberty.jpg"),
        ]
        db.session.bulk_save_objects(attractions)
        print(f"Seeded {len(attractions)} attractions.")

        # Create Posts
        posts = [
            Post(id=1, user_id=1, content="This is the first post by user 1."),
            Post(id=2, user_id=1, content="This is the second post by user 1."),
            Post(id=3, user_id=2, content="This is the first post by user 2."),
        ]
        db.session.bulk_save_objects(posts)
        print(f"Seeded {len(posts)} posts.")

        # Create VideoPosts
        video_posts = [
            VideoPost(id=1, user_id=1, title="My trip to Paris", video_url="https://example.com/paris.mp4"),
            VideoPost(id=2, user_id=2, title="New York adventure", video_url="https://example.com/newyork.mp4"),
        ]
        db.session.bulk_save_objects(video_posts)
        print(f"Seeded {len(video_posts)} video posts.")

        # Create some engagement data
        likes = [
            Like(user_id=1, post_id=3), # user 1 likes post 3
            Like(user_id=2, post_id=1), # user 2 likes post 1
            Like(user_id=1, video_post_id=2), # user 1 likes video 2
        ]
        db.session.bulk_save_objects(likes)
        print(f"Seeded {len(likes)} likes.")

        comments = [
            Comment(user_id=2, post_id=1, content="Great post!"),
            Comment(user_id=1, post_id=3, content="Nice!"),
        ]
        db.session.bulk_save_objects(comments)
        print(f"Seeded {len(comments)} comments.")


        db.session.commit()
        print("Database seeded successfully.")

if __name__ == "__main__":
    seed_database()
