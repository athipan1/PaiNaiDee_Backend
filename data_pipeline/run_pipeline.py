import os
import sys
import logging
import requests
from supabase import create_client, Client
from dotenv import load_dotenv

# Add the project root to the Python path to allow imports from 'app' and 'src'
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Import the fetcher from our sources module
from data_pipeline.sources.mock_source import fetch_data

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("data_pipeline.log"),
        logging.StreamHandler()
    ]
)

# --- Configuration & Supabase Client ---
# Load environment variables from .env file
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    logging.error("Supabase URL and Key must be set in environment variables.")
    sys.exit(1)

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    logging.info("Successfully connected to Supabase.")
except Exception as e:
    logging.error(f"Failed to connect to Supabase: {e}")
    sys.exit(1)

def upload_image_to_storage(image_url: str, source_name: str, source_id: str) -> str | None:
    """
    Downloads an image from a URL and uploads it to Supabase storage.

    Args:
        image_url: The URL of the image to download.
        source_name: The name of the data source (e.g., 'mock_source').
        source_id: The unique ID of the attraction from the source.

    Returns:
        The public URL of the uploaded image, or None on failure.
    """
    if not image_url:
        return None

    try:
        response = requests.get(image_url, timeout=15)
        response.raise_for_status()  # Raise an exception for bad status codes
        image_data = response.content
    except requests.RequestException as e:
        logging.error(f"Failed to download image {image_url}: {e}")
        return None

    # Create a unique path for the image in storage
    file_extension = os.path.splitext(image_url)[1]
    if not file_extension:
        file_extension = '.jpg' # Default to .jpg if no extension found
    storage_path = f"{source_name}/{source_id}{file_extension}"

    try:
        # Use upsert=True to avoid errors if the file already exists
        supabase.storage.from_("attractions").upload(
            path=storage_path,
            file=image_data,
            file_options={"upsert": True, "content-type": "image/jpeg"}
        )
        public_url = supabase.storage.from_("attractions").get_public_url(storage_path)
        logging.info(f"Successfully uploaded image to {public_url}")
        return public_url
    except Exception as e:
        logging.error(f"Failed to upload image to Supabase storage: {e}")
        return None

def transform_data(raw_data: dict, source_name: str) -> dict | None:
    """
    Transforms a raw attraction record into the database schema format.
    """
    if not raw_data.get('name') or not raw_data.get('place_id'):
        logging.warning(f"Skipping record due to missing name or place_id: {raw_data}")
        return None

    details = raw_data.get('details', {})
    location = raw_data.get('location', {})

    # Extract main image and other images
    main_image_source_url = None
    other_image_urls = []
    if raw_data.get('images'):
        for img in raw_data['images']:
            if img.get('is_main'):
                main_image_source_url = img.get('url')
            else:
                other_image_urls.append(img.get('url'))

    return {
        "name": raw_data.get('name'),
        "description": raw_data.get('description'),
        "province": details.get('province'),
        "district": details.get('district'),
        "latitude": location.get('lat'),
        "longitude": location.get('lng'),
        "category": details.get('category'),
        "opening_hours": details.get('opening_hours'),
        "entrance_fee": details.get('fee'),
        "contact_phone": details.get('phone'),
        "website": details.get('website'),
        "source": source_name,
        "source_id": raw_data.get('place_id'),
        # Image URLs are handled separately after upload
        "main_image_url": None,
        "image_urls": other_image_urls,
        # This is not part of the DB schema, but useful for the pipeline
        "_source_main_image_url": main_image_source_url
    }

def main():
    """The main function to run the data pipeline."""
    logging.info("Starting data pipeline...")

    # This will be expanded in the next steps
    raw_attractions = fetch_data()
    if not raw_attractions:
        logging.warning("No data fetched. Exiting pipeline.")
        return

    logging.info(f"Fetched {len(raw_attractions)} raw attraction records.")

    for raw_attraction in raw_attractions:
        source_name = "mock_source" # This would be dynamic for multiple sources
        logging.info(f"Processing '{raw_attraction.get('name')}' from source '{source_name}'")

        # 1. Transform data
        clean_data = transform_data(raw_attraction, source_name)
        if not clean_data:
            continue

        # 2. Upload main image
        main_image_url_to_upload = clean_data.pop("_source_main_image_url", None)
        if main_image_url_to_upload:
            uploaded_image_url = upload_image_to_storage(
                image_url=main_image_url_to_upload,
                source_name=source_name,
                source_id=clean_data["source_id"]
            )
            clean_data["main_image_url"] = uploaded_image_url

        # 3. Upsert record
        try:
            # The 'on_conflict' parameter should match the unique constraint in the database
            response = supabase.table("attractions").upsert(
                clean_data,
                on_conflict="source,source_id"
            ).execute()
            logging.info(f"Successfully upserted '{clean_data['name']}'.")
        except Exception as e:
            logging.error(f"Failed to upsert '{clean_data['name']}': {e}")

    logging.info("Data pipeline finished.")


if __name__ == "__main__":
    main()
