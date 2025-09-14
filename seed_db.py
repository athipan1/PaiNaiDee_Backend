import asyncio
from typing import List

from sqlalchemy import text
from app.db.session import AsyncSessionLocal, async_engine
from app.db.models import Base, Location, Post, PostMedia


async def seed_phase1():
    # Ensure tables (UUID schema) exist for Phase 1 models
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed sample data
    async with AsyncSessionLocal() as db:
        # Clean previous sample data (PostgreSQL only). Safe to skip if not Postgres or tables missing.
        try:
            await db.execute(
                text("TRUNCATE TABLE post_media, posts, locations RESTART IDENTITY CASCADE;")
            )
            await db.commit()
        except Exception:
            await db.rollback()

        # Create Locations
        locations: List[Location] = [
            Location(name="วัดพระแก้ว", province="กรุงเทพมหานคร", lat=13.7515, lng=100.4929),
            Location(name="ดอยสุเทพ", province="เชียงใหม่", lat=18.8049, lng=98.9215),
            Location(name="เกาะพีพี", province="กระบี่", lat=7.7407, lng=98.7784),
        ]
        for loc in locations:
            db.add(loc)
        await db.flush()  # get UUIDs

        # Create Posts
        posts: List[Post] = [
            Post(
                user_id="demo_user_1",
                caption="เช็คอินวัดพระแก้ว สวยมาก",
                tags=["temple", "bangkok", "culture"],
                location_id=locations[0].id,
                lat=locations[0].lat,
                lng=locations[0].lng,
            ),
            Post(
                user_id="demo_user_2",
                caption="วิวดอยสุเทพสุดปัง",
                tags=["mountain", "chiangmai", "nature"],
                location_id=locations[1].id,
                lat=locations[1].lat,
                lng=locations[1].lng,
            ),
            Post(
                user_id="demo_user_3",
                caption="เกาะพีพี น้ำทะเลใสมาก",
                tags=["beach", "krabi", "island"],
                location_id=locations[2].id,
                lat=locations[2].lat,
                lng=locations[2].lng,
            ),
        ]
        for p in posts:
            db.add(p)
        await db.flush()  # get post UUIDs

        # Create Media
        media_entries: List[PostMedia] = [
            PostMedia(
                post_id=posts[0].id,
                media_type="image",
                url="https://example.com/images/wat_phra_kaew_1.jpg",
                thumb_url="https://example.com/images/wat_phra_kaew_1_thumb.jpg",
                ordering=0,
            ),
            PostMedia(
                post_id=posts[1].id,
                media_type="image",
                url="https://example.com/images/doi_suthep_1.jpg",
                thumb_url="https://example.com/images/doi_suthep_1_thumb.jpg",
                ordering=0,
            ),
            PostMedia(
                post_id=posts[2].id,
                media_type="image",
                url="https://example.com/images/phi_phi_1.jpg",
                thumb_url="https://example.com/images/phi_phi_1_thumb.jpg",
                ordering=0,
            ),
        ]
        for m in media_entries:
            db.add(m)

        await db.commit()
        print("Database seeded successfully for Phase 1 (UUID schema).")


def main():
    asyncio.run(seed_phase1())


if __name__ == "__main__":
    main()
