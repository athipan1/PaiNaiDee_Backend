import json
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.logging import logger
from app.db.models import Location, Post, PostMedia
from app.core.config import settings

async def seed_data(db: AsyncSession):
    """
    Seeds the database with initial data from a JSON file if the database is empty.
    """
    logger.log_event("db.seeding.check", {"message": "Checking if database needs seeding."})

    # 1. Check if Locations table is empty
    result = await db.execute(select(Location))
    if result.scalars().first() is not None:
        logger.log_event("db.seeding.skipped", {"message": "Database already seeded."})
        return

    logger.log_event("db.seeding.start", {"message": "Database is empty. Seeding data..."})

    # 2. Load data from JSON file
    try:
        with open(settings.attractions_json_path, "r", encoding="utf-8-sig") as f:
            attractions = json.load(f)
        logger.log_event("db.seeding.load_json.success", {"count": len(attractions), "path": settings.attractions_json_path})
    except FileNotFoundError:
        logger.log_event("db.seeding.load_json.failed", {"error": "File not found", "path": settings.attractions_json_path})
        return
    except json.JSONDecodeError:
        logger.log_event("db.seeding.load_json.failed", {"error": "JSON decode error", "path": settings.attractions_json_path})
        return

    # 3. Create and add new objects to the session
    for attraction in attractions:
        # Create Location
        new_location = Location(
            name=attraction.get("name"),
            province=attraction.get("province"),
            lat=attraction.get("latitude") or 0.0,
            lng=attraction.get("longitude") or 0.0,
            popularity_score=0 # Default value
        )
        db.add(new_location)
        await db.flush() # Flush to get the new_location.id

        # Create Post
        new_post = Post(
            user_id="system_generated", # Placeholder user
            caption=attraction.get("description", ""),
            location_id=new_location.id,
            lat=new_location.lat,
            lng=new_location.lng,
            tags=[attraction.get("category")] if attraction.get("category") else []
        )
        db.add(new_post)
        await db.flush() # Flush to get the new_post.id

        # Create PostMedia
        image_urls = attraction.get("image_urls", [])
        if image_urls and isinstance(image_urls, list) and "value" in image_urls[0]:
             for i, url in enumerate(image_urls[0]["value"]):
                new_media = PostMedia(
                    post_id=new_post.id,
                    media_type="image",
                    url=url,
                    ordering=i
                )
                db.add(new_media)


    # 4. Commit the transaction
    try:
        await db.commit()
        logger.log_event("db.seeding.commit.success", {"message": "Successfully seeded database."})
    except Exception as e:
        logger.log_event("db.seeding.commit.failed", {"error": str(e)})
        await db.rollback()
