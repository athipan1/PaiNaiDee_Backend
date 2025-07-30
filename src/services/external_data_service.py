"""
External Data Integration Service for Tourism Places

This service handles fetching, parsing, and updating tourism data from external sources.
Supports multiple data sources including Google Places API, TAT, and other APIs.
"""

import requests
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import json
import time
from urllib.parse import urljoin

from src.models import db, Attraction
from src.models.attraction import Attraction as AttractionModel


@dataclass
class ExternalDataSource:
    """Configuration for an external data source"""
    name: str
    base_url: str
    api_key: Optional[str] = None
    headers: Optional[Dict[str, str]] = None
    rate_limit_per_second: float = 1.0
    enabled: bool = True


@dataclass
class AttractionData:
    """Standardized attraction data from external sources"""
    external_id: str
    name: str
    description: str
    province: str
    district: str = ""
    address: str = ""
    latitude: float = 0.0
    longitude: float = 0.0
    category: str = ""
    opening_hours: str = ""
    entrance_fee: str = ""
    contact_phone: str = ""
    website: str = ""
    main_image_url: str = ""
    image_urls: List[str] = None
    source: str = ""
    last_updated: datetime = None

    def __post_init__(self):
        if self.image_urls is None:
            self.image_urls = []
        if self.last_updated is None:
            self.last_updated = datetime.utcnow()


@dataclass
class UpdateResult:
    """Result of data update operation"""
    success: bool
    total_processed: int = 0
    new_created: int = 0
    existing_updated: int = 0
    errors: List[str] = None
    source: str = ""
    timestamp: datetime = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


class ExternalDataService:
    """Service for managing external tourism data sources"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.data_sources = self._initialize_data_sources()
        self.last_request_time = {}
        self.update_history = []

    def _initialize_data_sources(self) -> Dict[str, ExternalDataSource]:
        """Initialize configured external data sources"""
        sources = {
            'google_places': ExternalDataSource(
                name="Google Places API",
                base_url="https://maps.googleapis.com/maps/api/place/",
                rate_limit_per_second=0.1,  # Conservative rate limiting
                enabled=False  # Disabled by default - requires API key
            ),
            'tat_api': ExternalDataSource(
                name="Tourism Authority of Thailand",
                base_url="https://tatapi.tourismthailand.org/",
                rate_limit_per_second=0.5,
                enabled=True
            ),
            'tripadvisor': ExternalDataSource(
                name="TripAdvisor Content API",
                base_url="https://api.content.tripadvisor.com/api/v1/",
                rate_limit_per_second=0.2,
                enabled=False  # Disabled by default - requires API key
            )
        }
        return sources

    def configure_source(self, source_name: str, api_key: str = None, 
                        enabled: bool = True, headers: Dict[str, str] = None):
        """Configure an external data source"""
        if source_name in self.data_sources:
            source = self.data_sources[source_name]
            if api_key:
                source.api_key = api_key
            source.enabled = enabled
            if headers:
                source.headers = headers
            self.logger.info(f"Configured data source: {source_name}")
        else:
            self.logger.warning(f"Unknown data source: {source_name}")

    def _rate_limit(self, source_name: str):
        """Apply rate limiting for API requests"""
        source = self.data_sources.get(source_name)
        if not source:
            return

        last_request = self.last_request_time.get(source_name, 0)
        min_interval = 1.0 / source.rate_limit_per_second
        elapsed = time.time() - last_request
        
        if elapsed < min_interval:
            sleep_time = min_interval - elapsed
            time.sleep(sleep_time)
        
        self.last_request_time[source_name] = time.time()

    def fetch_from_google_places(self, query: str = "", location: str = "", 
                                radius: int = 50000) -> List[AttractionData]:
        """Fetch tourism data from Google Places API"""
        source_name = 'google_places'
        source = self.data_sources[source_name]
        
        if not source.enabled or not source.api_key:
            self.logger.warning("Google Places API is not enabled or configured")
            return []

        attractions = []
        try:
            # Search for tourist attractions
            search_url = urljoin(source.base_url, "textsearch/json")
            params = {
                'query': f"tourist attractions {query} {location} Thailand",
                'key': source.api_key,
                'radius': radius,
                'type': 'tourist_attraction'
            }
            
            self._rate_limit(source_name)
            response = requests.get(search_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            for place in data.get('results', []):
                attraction_data = self._parse_google_place(place, source_name)
                if attraction_data:
                    attractions.append(attraction_data)
                    
        except Exception as e:
            self.logger.error(f"Error fetching from Google Places: {e}")
            
        return attractions

    def fetch_from_tat_api(self, province: str = "") -> List[AttractionData]:
        """Fetch tourism data from TAT API (mock implementation)"""
        source_name = 'tat_api'
        source = self.data_sources[source_name]
        
        if not source.enabled:
            return []

        attractions = []
        try:
            # Note: This is a mock implementation as TAT API structure is not publicly documented
            # In real implementation, this would use actual TAT API endpoints
            
            # For demonstration, we'll parse existing JSON data as if it came from TAT
            tat_data = self._get_mock_tat_data(province)
            
            for place_data in tat_data:
                attraction_data = self._parse_tat_place(place_data, source_name)
                if attraction_data:
                    attractions.append(attraction_data)
                    
        except Exception as e:
            self.logger.error(f"Error fetching from TAT API: {e}")
            
        return attractions

    def fetch_from_tripadvisor(self, location: str = "Thailand") -> List[AttractionData]:
        """Fetch tourism data from TripAdvisor Content API"""
        source_name = 'tripadvisor'
        source = self.data_sources[source_name]
        
        if not source.enabled or not source.api_key:
            self.logger.warning("TripAdvisor API is not enabled or configured")
            return []

        attractions = []
        try:
            # Search for attractions
            search_url = urljoin(source.base_url, "location/search")
            headers = {
                'X-TripAdvisor-API-Key': source.api_key,
                'Accept': 'application/json'
            }
            if source.headers:
                headers.update(source.headers)
            
            params = {
                'searchQuery': f"attractions {location}",
                'category': 'attractions',
                'language': 'en'
            }
            
            self._rate_limit(source_name)
            response = requests.get(search_url, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            for place in data.get('data', []):
                attraction_data = self._parse_tripadvisor_place(place, source_name)
                if attraction_data:
                    attractions.append(attraction_data)
                    
        except Exception as e:
            self.logger.error(f"Error fetching from TripAdvisor: {e}")
            
        return attractions

    def _parse_google_place(self, place_data: Dict, source: str) -> Optional[AttractionData]:
        """Parse Google Places API response into AttractionData"""
        try:
            geometry = place_data.get('geometry', {})
            location = geometry.get('location', {})
            
            # Get photos
            photos = place_data.get('photos', [])
            image_urls = []
            main_image_url = ""
            
            if photos:
                # Note: In real implementation, you'd need to construct photo URLs
                # using the Places API photo reference
                main_image_url = f"google_photo_{photos[0].get('photo_reference', '')}"
                image_urls = [f"google_photo_{photo.get('photo_reference', '')}" 
                            for photo in photos[:5]]

            return AttractionData(
                external_id=f"google_{place_data.get('place_id', '')}",
                name=place_data.get('name', ''),
                description=place_data.get('editorial_summary', {}).get('overview', ''),
                province=self._extract_province_from_address(
                    place_data.get('formatted_address', '')
                ),
                address=place_data.get('formatted_address', ''),
                latitude=location.get('lat', 0.0),
                longitude=location.get('lng', 0.0),
                category=self._categorize_place(place_data.get('types', [])),
                opening_hours=self._format_opening_hours(
                    place_data.get('opening_hours', {})
                ),
                contact_phone=place_data.get('formatted_phone_number', ''),
                website=place_data.get('website', ''),
                main_image_url=main_image_url,
                image_urls=image_urls,
                source=source
            )
        except Exception as e:
            self.logger.error(f"Error parsing Google place data: {e}")
            return None

    def _parse_tat_place(self, place_data: Dict, source: str) -> Optional[AttractionData]:
        """Parse TAT API response into AttractionData"""
        try:
            # Handle image URLs - convert from existing format
            image_urls = []
            main_image_url = place_data.get('main_image_url', '')
            
            if place_data.get('image_urls'):
                if isinstance(place_data['image_urls'], list):
                    for img_entry in place_data['image_urls']:
                        if isinstance(img_entry, dict) and 'value' in img_entry:
                            image_urls.extend(img_entry['value'])
                        elif isinstance(img_entry, str):
                            image_urls.append(img_entry)

            return AttractionData(
                external_id=f"tat_{place_data.get('id', '')}",
                name=place_data.get('name', ''),
                description=place_data.get('description', ''),
                province=place_data.get('province', ''),
                district=place_data.get('district', ''),
                address=place_data.get('address', ''),
                latitude=float(place_data.get('latitude', 0)),
                longitude=float(place_data.get('longitude', 0)),
                category=place_data.get('category', ''),
                opening_hours=place_data.get('opening_hours', ''),
                entrance_fee=place_data.get('entrance_fee', ''),
                contact_phone=place_data.get('contact_phone', ''),
                website=place_data.get('website', ''),
                main_image_url=main_image_url,
                image_urls=image_urls,
                source=source
            )
        except Exception as e:
            self.logger.error(f"Error parsing TAT place data: {e}")
            return None

    def _parse_tripadvisor_place(self, place_data: Dict, source: str) -> Optional[AttractionData]:
        """Parse TripAdvisor API response into AttractionData"""
        try:
            location_data = place_data.get('location', {})
            
            return AttractionData(
                external_id=f"tripadvisor_{place_data.get('location_id', '')}",
                name=place_data.get('name', ''),
                description=place_data.get('description', ''),
                province=self._extract_province_from_address(
                    location_data.get('address', '')
                ),
                address=location_data.get('address', ''),
                latitude=float(location_data.get('latitude', 0)),
                longitude=float(location_data.get('longitude', 0)),
                category=self._categorize_place(place_data.get('category', [])),
                main_image_url=place_data.get('photo', {}).get('images', {}).get('large', {}).get('url', ''),
                source=source
            )
        except Exception as e:
            self.logger.error(f"Error parsing TripAdvisor place data: {e}")
            return None

    def _get_mock_tat_data(self, province: str = "") -> List[Dict]:
        """Get mock TAT data from existing JSON files"""
        try:
            import os
            from pathlib import Path
            
            # Try to load from existing JSON files
            project_root = Path(__file__).parent.parent.parent
            json_files = [
                project_root / "attractions_cleaned_from_api.json",
                project_root / "attractions_cleaned_ready.json"
            ]
            
            all_data = []
            for json_file in json_files:
                if json_file.exists():
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if isinstance(data, list):
                            all_data.extend(data)
                        
            # Filter by province if specified
            if province:
                all_data = [item for item in all_data 
                          if item.get('province', '').lower() == province.lower()]
                          
            return all_data
            
        except Exception as e:
            self.logger.error(f"Error loading mock TAT data: {e}")
            return []

    def update_attractions_from_source(self, source_name: str, 
                                     **kwargs) -> UpdateResult:
        """Update attractions from a specific external source"""
        result = UpdateResult(success=False, source=source_name)
        
        try:
            # Fetch data from the specified source
            attractions_data = []
            
            if source_name == 'google_places':
                attractions_data = self.fetch_from_google_places(**kwargs)
            elif source_name == 'tat_api':
                attractions_data = self.fetch_from_tat_api(**kwargs)
            elif source_name == 'tripadvisor':
                attractions_data = self.fetch_from_tripadvisor(**kwargs)
            else:
                result.errors.append(f"Unknown source: {source_name}")
                return result
            
            result.total_processed = len(attractions_data)
            
            # Process each attraction
            for attraction_data in attractions_data:
                try:
                    created, updated = self._upsert_attraction(attraction_data)
                    if created:
                        result.new_created += 1
                    elif updated:
                        result.existing_updated += 1
                        
                except Exception as e:
                    error_msg = f"Error processing {attraction_data.name}: {e}"
                    result.errors.append(error_msg)
                    self.logger.error(error_msg)
            
            result.success = True
            self.update_history.append(result)
            
        except Exception as e:
            error_msg = f"Error updating from {source_name}: {e}"
            result.errors.append(error_msg)
            self.logger.error(error_msg)
            
        return result

    def _upsert_attraction(self, attraction_data: AttractionData) -> Tuple[bool, bool]:
        """Insert or update attraction in database"""
        created = False
        updated = False
        
        try:
            # Look for existing attraction by name and province (fuzzy matching)
            existing = self._find_existing_attraction(attraction_data)
            
            if existing:
                # Update existing attraction
                updated = self._update_existing_attraction(existing, attraction_data)
            else:
                # Create new attraction
                created = self._create_new_attraction(attraction_data)
                
        except Exception as e:
            self.logger.error(f"Error in upsert operation: {e}")
            raise
            
        return created, updated

    def _find_existing_attraction(self, attraction_data: AttractionData) -> Optional[AttractionModel]:
        """Find existing attraction using fuzzy matching"""
        # Try exact name match first
        existing = AttractionModel.query.filter(
            AttractionModel.name == attraction_data.name,
            AttractionModel.province == attraction_data.province
        ).first()
        
        if existing:
            return existing
        
        # Try fuzzy name matching (similar names in same province)
        similar_attractions = AttractionModel.query.filter(
            AttractionModel.province == attraction_data.province
        ).all()
        
        for attraction in similar_attractions:
            similarity = self._calculate_similarity(
                attraction.name, attraction_data.name
            )
            if similarity > 0.8:  # 80% similarity threshold
                return attraction
                
        return None

    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """Calculate similarity between two strings"""
        from difflib import SequenceMatcher
        return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()

    def _update_existing_attraction(self, existing: AttractionModel, 
                                  new_data: AttractionData) -> bool:
        """Update existing attraction with new data"""
        updated = False
        
        try:
            # Update fields if new data is more complete
            updates = {}
            
            if new_data.description and len(new_data.description) > len(existing.description or ""):
                updates['description'] = new_data.description
                
            if new_data.address and not existing.address:
                updates['address'] = new_data.address
                
            if new_data.latitude and new_data.longitude:
                if not existing.latitude or not existing.longitude:
                    updates['latitude'] = new_data.latitude
                    updates['longitude'] = new_data.longitude
                    
            if new_data.category and not existing.category:
                updates['category'] = new_data.category
                
            if new_data.opening_hours and not existing.opening_hours:
                updates['opening_hours'] = new_data.opening_hours
                
            if new_data.entrance_fee and not existing.entrance_fee:
                updates['entrance_fee'] = new_data.entrance_fee
                
            if new_data.contact_phone and not existing.contact_phone:
                updates['contact_phone'] = new_data.contact_phone
                
            if new_data.website and not existing.website:
                updates['website'] = new_data.website
            
            # Update images if new ones are available
            if new_data.main_image_url and not existing.main_image_url:
                updates['main_image_url'] = new_data.main_image_url
                
            if new_data.image_urls:
                # Merge image URLs (avoid duplicates)
                existing_images = existing.image_urls or []
                if isinstance(existing_images, dict) and 'value' in existing_images:
                    existing_images = existing_images['value']
                elif not isinstance(existing_images, list):
                    existing_images = []
                    
                new_images = list(set(existing_images + new_data.image_urls))
                if len(new_images) > len(existing_images):
                    updates['image_urls'] = new_images
            
            # Apply updates
            if updates:
                for field, value in updates.items():
                    setattr(existing, field, value)
                
                db.session.commit()
                updated = True
                self.logger.info(f"Updated attraction: {existing.name}")
                
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error updating attraction {existing.name}: {e}")
            raise
            
        return updated

    def _create_new_attraction(self, attraction_data: AttractionData) -> bool:
        """Create new attraction from external data"""
        try:
            new_attraction = AttractionModel(
                name=attraction_data.name,
                description=attraction_data.description,
                address=attraction_data.address,
                province=attraction_data.province,
                district=attraction_data.district,
                latitude=attraction_data.latitude,
                longitude=attraction_data.longitude,
                category=attraction_data.category,
                opening_hours=attraction_data.opening_hours,
                entrance_fee=attraction_data.entrance_fee,
                contact_phone=attraction_data.contact_phone,
                website=attraction_data.website,
                main_image_url=attraction_data.main_image_url,
                image_urls=attraction_data.image_urls
            )
            
            db.session.add(new_attraction)
            db.session.commit()
            
            self.logger.info(f"Created new attraction: {attraction_data.name}")
            return True
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error creating attraction {attraction_data.name}: {e}")
            raise

    def update_all_sources(self, **kwargs) -> List[UpdateResult]:
        """Update attractions from all enabled sources"""
        results = []
        
        for source_name, source in self.data_sources.items():
            if source.enabled:
                self.logger.info(f"Updating from source: {source_name}")
                result = self.update_attractions_from_source(source_name, **kwargs)
                results.append(result)
            else:
                self.logger.info(f"Skipping disabled source: {source_name}")
                
        return results

    def get_update_history(self, limit: int = 10) -> List[UpdateResult]:
        """Get recent update history"""
        return self.update_history[-limit:]

    def get_source_status(self) -> Dict[str, Dict]:
        """Get status of all data sources"""
        status = {}
        for name, source in self.data_sources.items():
            status[name] = {
                'enabled': source.enabled,
                'configured': source.api_key is not None if source.name != "Tourism Authority of Thailand" else True,
                'rate_limit': source.rate_limit_per_second,
                'last_request': self.last_request_time.get(name)
            }
        return status

    def _extract_province_from_address(self, address: str) -> str:
        """Extract Thai province from address string"""
        thai_provinces = [
            'กรุงเทพมหานคร', 'กระบี่', 'กาญจนบุรี', 'กาฬสินธุ์', 'กำแพงเพชร',
            'ขอนแก่น', 'จันทบุรี', 'ฉะเชิงเทรา', 'ชลบุรี', 'ชัยนาท', 'ชัยภูมิ',
            'ชุมพร', 'เชียงราย', 'เชียงใหม่', 'ตรัง', 'ตราด', 'ตาก', 'นครนายก',
            'นครปฐม', 'นครพนม', 'นครราชสีมา', 'นครศรีธรรมราช', 'นครสวรรค์',
            'นนทบุรี', 'นราธิวาส', 'น่าน', 'บึงกาฬ', 'บุรีรัมย์', 'ปทุมธานี',
            'ประจวบคีรีขันธ์', 'ปราจีนบุรี', 'ปัตตานี', 'พระนครศรีอยุธยา',
            'พังงา', 'พัทลุง', 'พิจิตร', 'พิษณุโลก', 'เพชรบุรี', 'เพชรบูรณ์',
            'แพร่', 'ภูเก็ต', 'มหาสารคาม', 'มุกดาหาร', 'แม่ฮ่องสอน', 'ยโสธร',
            'ยะลา', 'ร้อยเอ็ด', 'ระนอง', 'ระยอง', 'ราชบุรี', 'ลพบุรี', 'ลำปาง',
            'ลำพูน', 'เลย', 'ศรีสะเกษ', 'สกลนคร', 'สงขลา', 'สตูล', 'สมุทรปราการ',
            'สมุทรสงคราม', 'สมุทรสาคร', 'สระแก้ว', 'สระบุรี', 'สิงห์บุรี',
            'สุโขทัย', 'สุพรรณบุรี', 'สุราษฎร์ธานี', 'สุรินทร์', 'หนองคาย',
            'หนองบัวลำภู', 'อ่างทอง', 'อำนาจเจริญ', 'อุดรธานี', 'อุตรดิตถ์',
            'อุทัยธานี', 'อุบลราชธานี'
        ]
        
        for province in thai_provinces:
            if province in address:
                return province
                
        # English province names mapping
        english_to_thai = {
            'bangkok': 'กรุงเทพมหานคร',
            'krabi': 'กระบี่',
            'chiang mai': 'เชียงใหม่',
            'phuket': 'ภูเก็ต',
            'chonburi': 'ชลบุรี'
        }
        
        address_lower = address.lower()
        for eng_name, thai_name in english_to_thai.items():
            if eng_name in address_lower:
                return thai_name
                
        return ""

    def _categorize_place(self, types_or_category) -> str:
        """Categorize place based on types or category"""
        if isinstance(types_or_category, list):
            types = [t.lower() for t in types_or_category]
        else:
            types = [str(types_or_category).lower()]
            
        # Category mapping - order matters for priority (specific to general)
        category_mapping = [
            ('temple', 'วัด'),
            ('religious', 'วัด'),
            ('place_of_worship', 'วัด'),
            ('beach', 'ชายหาด'),
            ('mountain', 'ภูเขา'),
            ('natural_feature', 'ธรรมชาติ'),
            ('museum', 'พิพิธภัณฑ์'),
            ('park', 'สวนสาธารณะ'),
            ('cultural', 'วัฒนธรรม'),
            ('tourist_attraction', 'สถานที่ท่องเที่ยว')
        ]
        
        # Check each mapping in priority order
        for keyword, category in category_mapping:
            for type_name in types:
                if keyword in type_name:
                    return category
                    
        return 'สถานที่ท่องเที่ยว'  # Default category

    def _format_opening_hours(self, opening_hours_data) -> str:
        """Format opening hours from various API formats"""
        if isinstance(opening_hours_data, dict):
            if 'weekday_text' in opening_hours_data:
                return '\n'.join(opening_hours_data['weekday_text'])
        elif isinstance(opening_hours_data, str):
            return opening_hours_data
            
        return ""