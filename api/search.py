from flask import Flask, request, jsonify
from flask_cors import CORS
import re
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from difflib import SequenceMatcher
import unicodedata

app = Flask(__name__)
CORS(app)


@dataclass
class SearchQuery:
    query: str
    language: str
    filters: Dict[str, List[str]]


@dataclass
class SearchResult:
    id: str
    name: str
    name_local: str
    province: str
    category: str
    tags: List[str]
    rating: float
    review_count: int
    image: str
    description: str
    confidence: float
    matched_terms: List[str]
    amenities: List[str] = None
    location: Dict[str, float] = None


@dataclass
class SearchSuggestion:
    id: str
    type: str
    text: str
    description: str
    confidence: float
    province: str = None
    category: str = None
    image: str = None


class SearchEngine:
    def __init__(self):
        self.places_data = [
            {
                "id": "1",
                "name": "Phi Phi Islands",
                "name_local": "เกาะพีพี",
                "province": "Krabi",
                "province_local": "กระบี่",
                "category": "Beach",
                "tags": ["Beach", "Snorkeling", "Island", "Photography"],
                "tags_local": ["ชายหาด", "ดำน้ำดูปะการัง", "เกาะ", "ถ่ายรูป"],
                "rating": 4.8,
                "review_count": 2547,
                "image": "https://images.pexels.com/photos/1450353/pexels-photo-1450353.jpeg?auto=compress&cs=tinysrgb&w=400",
                "description": {
                    "th": (
                        "น้ำทะเลใสและหน้าผาหินปูนที่สวยงาม "
                        "ทำให้ที่นี่เป็นสวรรค์สำหรับผู้ที่ชื่นชอบชายหาดและการดำน้ำดูปะการัง"
                    ),
                    "en": (
                        "Crystal clear waters and stunning limestone cliffs make this "
                        "a paradise for beach lovers and snorkeling enthusiasts."
                    ),
                },
                "amenities": [
                    "Restaurant",
                    "Boat Tours",
                    "Snorkeling Equipment",
                    "Beach Chairs",
                ],
                "location": {"lat": 7.7407, "lng": 98.7784},
            },
            {
                "id": "2",
                "name": "Wat Phra Kaew",
                "name_local": "วัดพระแก้ว",
                "province": "Bangkok",
                "province_local": "กรุงเทพฯ",
                "category": "Culture",
                "tags": ["Temple", "Culture", "Buddhism", "History"],
                "tags_local": ["วัด", "วัฒนธรรม", "พุทธศาสนา", "ประวัติศาสตร์"],
                "rating": 4.9,
                "review_count": 5243,
                "image": "https://images.pexels.com/photos/2614818/pexels-photo-2614818.jpeg?auto=compress&cs=tinysrgb&w=400",
                "description": {
                    "th": (
                        "วัดที่ศักดิ์สิทธิ์ที่สุดในประเทศไทย "
                        "เป็นที่ประดิษฐานของพระแก้วมรกต"
                    ),
                    "en": (
                        "The most sacred Buddhist temple in Thailand, "
                        "home to the revered Emerald Buddha statue."
                    ),
                },
                "amenities": ["Audio Guide", "Gift Shop", "Guided Tours", "Parking"],
                "location": {"lat": 13.7515, "lng": 100.4925},
            },
            {
                "id": "3",
                "name": "Doi Inthanon",
                "name_local": "ดอยอินทนนท์",
                "province": "Chiang Mai",
                "province_local": "เชียงใหม่",
                "category": "Nature",
                "tags": ["Mountain", "Nature", "Hiking", "Waterfalls"],
                "tags_local": ["ภูเขา", "ธรรมชาติ", "เดินป่า", "น้ำตก"],
                "rating": 4.7,
                "review_count": 1876,
                "image": "https://images.pexels.com/photos/1450360/pexels-photo-1450360.jpeg?auto=compress&cs=tinysrgb&w=400",
                "description": {
                    "th": (
                        "ยอดเขาที่สูงที่สุดในประเทศไทย ชมวิวภูเขาที่งดงาม "
                        "น้ำตก และอากาศเย็นสบาย"
                    ),
                    "en": (
                        "The highest peak in Thailand offering breathtaking "
                        "mountain views, waterfalls, and cool weather."
                    ),
                },
                "amenities": [
                    "Hiking Trails",
                    "Visitor Center",
                    "Camping",
                    "Restaurant",
                ],
                "location": {"lat": 18.5889, "lng": 98.4867},
            },
            {
                "id": "4",
                "name": "Floating Market",
                "name_local": "ตลาดน้ำ",
                "province": "Bangkok",
                "province_local": "กรุงเทพฯ",
                "category": "Food",
                "tags": ["Food", "Culture", "Traditional", "Market"],
                "tags_local": ["อาหาร", "วัฒนธรรม", "แบบดั้งเดิม", "ตลาด"],
                "rating": 4.5,
                "review_count": 3156,
                "image": "https://images.pexels.com/photos/1450362/pexels-photo-1450362.jpeg?auto=compress&cs=tinysrgb&w=400",
                "description": {
                    "th": (
                        "สัมผัสวัฒนธรรมไทยแบบดั้งเดิม "
                        "ขณะช้อปปิ้งผลไม้สดและอาหารพื้นเมืองจากเรือ"
                    ),
                    "en": (
                        "Experience traditional Thai culture while shopping for "
                        "fresh fruits and local delicacies from boats."
                    ),
                },
                "amenities": ["Boat Tours", "Local Food", "Souvenirs", "Photography"],
                "location": {"lat": 13.7563, "lng": 100.5018},
            },
        ]

        self.provinces = [
            {"id": "bangkok", "name": "Bangkok", "name_local": "กรุงเทพฯ"},
            {"id": "krabi", "name": "Krabi", "name_local": "กระบี่"},
            {"id": "chiang-mai", "name": "Chiang Mai", "name_local": "เชียงใหม่"},
            {"id": "phuket", "name": "Phuket", "name_local": "ภูเก็ต"},
            {"id": "koh-samui", "name": "Koh Samui", "name_local": "เกาะสมุย"},
        ]

        self.categories = [
            {"id": "beach", "name": "Beach", "name_local": "ชายหาด"},
            {"id": "culture", "name": "Culture", "name_local": "วัฒนธรรม"},
            {"id": "nature", "name": "Nature", "name_local": "ธรรมชาติ"},
            {"id": "food", "name": "Food", "name_local": "อาหาร"},
            {"id": "mountain", "name": "Mountain", "name_local": "ภูเขา"},
        ]

        # Thai-specific search patterns
        self.thai_synonyms = {
            "ทะเล": ["ชายหาด", "หาด", "เกาะ"],
            "วัด": ["พระ", "โบสถ์", "ศาสนา"],
            "ภูเขา": ["ดอย", "เขา", "ยอด"],
            "อาหาร": ["กิน", "ตลาด", "ร้านอาหาร"],
            "ธรรมชาติ": ["ป่า", "น้ำตก", "สวน"],
        }

        self.english_synonyms = {
            "beach": ["sea", "ocean", "coast", "island"],
            "temple": ["wat", "buddhist", "religious", "sacred"],
            "mountain": ["hill", "peak", "summit", "doi"],
            "food": ["restaurant", "market", "cuisine", "dining"],
            "nature": ["forest", "waterfall", "park", "wildlife"],
        }

    def normalize_text(self, text: str) -> str:
        """Normalize text for better matching"""
        # Remove diacritics and convert to lowercase
        text = unicodedata.normalize("NFD", text.lower())
        text = "".join(
            c for c in text if unicodedata.category(c) != "Mn"
        )
        # Remove extra whitespace
        text = re.sub(r"\s+", " ", text.strip())
        return text

    def fuzzy_match(self, query: str, text: str) -> float:
        """Calculate fuzzy match score between query and text"""
        query_norm = self.normalize_text(query)
        text_norm = self.normalize_text(text)

        # Exact match
        if query_norm == text_norm:
            return 1.0

        # Contains match
        if query_norm in text_norm:
            return 0.8

        # Word boundary match
        query_words = query_norm.split()
        text_words = text_norm.split()

        match_count = 0
        for query_word in query_words:
            for text_word in text_words:
                if query_word in text_word or text_word in query_word:
                    match_count += 1
                    break

        word_match_ratio = match_count / len(query_words) if query_words else 0
        if word_match_ratio > 0.5:
            return 0.6 * word_match_ratio

        # Sequence matching
        similarity = SequenceMatcher(None, query_norm, text_norm).ratio()
        return similarity * 0.4 if similarity > 0.5 else 0

    def expand_query(self, query: str, language: str) -> List[str]:
        """Expand query with synonyms"""
        expanded = [query]
        query_lower = query.lower()

        synonyms = self.thai_synonyms if language == "th" else self.english_synonyms

        for key, values in synonyms.items():
            if key in query_lower:
                expanded.extend(values)
            for value in values:
                if value in query_lower:
                    expanded.append(key)

        return list(set(expanded))

    def analyze_query_intent(self, query: str, language: str) -> Dict[str, Any]:
        """Analyze search query to understand user intent"""
        intent = {
            "type": "general",
            "location_focused": False,
            "category_focused": False,
            "activity_focused": False,
            "keywords": [],
            "expanded_terms": [],
        }

        query_lower = query.lower()
        intent["expanded_terms"] = self.expand_query(query, language)

        # Location patterns
        location_patterns = {
            "th": ["จังหวัด", "ใน", "ที่", "แถว"],
            "en": ["in", "at", "near", "around", "province"],
        }

        for pattern in location_patterns.get(language, []):
            if pattern in query_lower:
                intent["location_focused"] = True
                break

        # Category patterns
        category_keywords = {
            "th": ["ชายหาด", "วัด", "ภูเขา", "อาหาร", "ธรรมชาติ"],
            "en": ["beach", "temple", "mountain", "food", "nature"],
        }

        for keyword in category_keywords.get(language, []):
            if keyword in query_lower:
                intent["category_focused"] = True
                intent["keywords"].append(keyword)

        # Activity patterns
        activity_keywords = {
            "th": ["เที่ยว", "ท่องเที่ยว", "เดิน", "ดำน้ำ", "ถ่ายรูป"],
            "en": ["visit", "tour", "hiking", "diving", "photography"],
        }

        for keyword in activity_keywords.get(language, []):
            if keyword in query_lower:
                intent["activity_focused"] = True
                intent["keywords"].append(keyword)

        return intent

    def search_places(
        self, search_query: SearchQuery
    ) -> Tuple[List[SearchResult], List[SearchSuggestion]]:
        """Search for places based on query and filters"""
        # Analyze query intent
        intent = self.analyze_query_intent(search_query.query, search_query.language)

        results = []
        suggestions = []

        # Search through places
        for place in self.places_data:
            # Get localized content
            name_to_search = (
                place["name_local"] if search_query.language == "th" else place["name"]
            )
            description_to_search = place["description"][search_query.language]
            tags_to_search = (
                place["tags_local"] if search_query.language == "th" else place["tags"]
            )
            province_to_search = (
                place["province_local"]
                if search_query.language == "th"
                else place["province"]
            )

            # Calculate confidence scores for different fields
            name_score = self.fuzzy_match(search_query.query, name_to_search)
            description_score = (
                self.fuzzy_match(search_query.query, description_to_search) * 0.7
            )
            province_score = (
                self.fuzzy_match(search_query.query, province_to_search) * 0.6
            )

            # Tag matching with expanded terms
            tag_scores = []
            for tag in tags_to_search:
                for term in intent["expanded_terms"]:
                    tag_scores.append(self.fuzzy_match(term, tag))
            tag_score = max(tag_scores) * 0.8 if tag_scores else 0

            # Calculate overall confidence
            confidence = max(name_score, description_score, tag_score, province_score)

            # Intent-based boosting
            if intent["category_focused"] and any(
                keyword in tags_to_search for keyword in intent["keywords"]
            ):
                confidence *= 1.2

            if intent["location_focused"] and province_score > 0.5:
                confidence *= 1.1

            # Minimum threshold
            if confidence > 0.3:
                # Apply filters
                passes_filter = True

                if search_query.filters.get("provinces"):
                    passes_filter = (
                        passes_filter
                        and place["province"].lower()
                        in [p.lower() for p in search_query.filters["provinces"]]
                    )

                if search_query.filters.get("categories"):
                    passes_filter = (
                        passes_filter
                        and place["category"].lower()
                        in [c.lower() for c in search_query.filters["categories"]]
                    )

                if search_query.filters.get("amenities"):
                    amenity_match = any(
                        amenity.lower()
                        in [a.lower() for a in place.get("amenities", [])]
                        for amenity in search_query.filters["amenities"]
                    )
                    passes_filter = passes_filter and amenity_match

                if passes_filter:
                    # Determine matched terms
                    matched_terms = []
                    if name_score > 0.3:
                        matched_terms.append(name_to_search)
                    if tag_score > 0.3:
                        matched_terms.extend(
                            [
                                tag
                                for tag in tags_to_search
                                if self.fuzzy_match(search_query.query, tag) > 0.3
                            ]
                        )

                    result = SearchResult(
                        id=place["id"],
                        name=place["name"],
                        name_local=place["name_local"],
                        province=province_to_search,
                        category=place["category"],
                        tags=tags_to_search,
                        rating=place["rating"],
                        review_count=place["review_count"],
                        image=place["image"],
                        description=description_to_search,
                        confidence=min(confidence, 1.0),  # Cap at 1.0
                        matched_terms=matched_terms,
                        amenities=place.get("amenities", []),
                        location=place.get("location"),
                    )
                    results.append(result)

        # Generate suggestions
        if len(search_query.query) > 0:
            # Place suggestions
            for place in self.places_data:
                name_to_search = (
                    place["name_local"]
                    if search_query.language == "th"
                    else place["name"]
                )
                score = self.fuzzy_match(search_query.query, name_to_search)

                if score > 0.4:
                    suggestion = SearchSuggestion(
                        id=f"place-{place['id']}",
                        type="place",
                        text=name_to_search,
                        description=place["province_local"]
                        if search_query.language == "th"
                        else place["province"],
                        confidence=score,
                        province=place["province_local"]
                        if search_query.language == "th"
                        else place["province"],
                        category=place["category"],
                        image=place["image"],
                    )
                    suggestions.append(suggestion)

            # Province suggestions
            for province in self.provinces:
                name_to_search = (
                    province["name_local"]
                    if search_query.language == "th"
                    else province["name"]
                )
                score = self.fuzzy_match(search_query.query, name_to_search)

                if score > 0.4:
                    suggestion = SearchSuggestion(
                        id=f"province-{province['id']}",
                        type="province",
                        text=name_to_search,
                        description="จังหวัด"
                        if search_query.language == "th"
                        else "Province",
                        confidence=score,
                    )
                    suggestions.append(suggestion)

            # Category suggestions
            for category in self.categories:
                name_to_search = (
                    category["name_local"]
                    if search_query.language == "th"
                    else category["name"]
                )
                score = self.fuzzy_match(search_query.query, name_to_search)

                if score > 0.4:
                    suggestion = SearchSuggestion(
                        id=f"category-{category['id']}",
                        type="category",
                        text=name_to_search,
                        description="หมวดหมู่"
                        if search_query.language == "th"
                        else "Category",
                        confidence=score,
                    )
                    suggestions.append(suggestion)

        # Sort by confidence
        results.sort(key=lambda x: x.confidence, reverse=True)
        suggestions.sort(key=lambda x: x.confidence, reverse=True)

        return results[:20], suggestions[:10]  # Limit results


# Initialize search engine
search_engine = SearchEngine()


@app.route("/api/search", methods=["POST"])
def search():
    """Main search endpoint"""
    try:
        data = request.get_json()

        search_query = SearchQuery(
            query=data.get("query", ""),
            language=data.get("language", "en"),
            filters=data.get("filters", {}),
        )

        results, suggestions = search_engine.search_places(search_query)

        # Convert dataclasses to dictionaries
        results_dict = []
        for result in results:
            results_dict.append(
                {
                    "id": result.id,
                    "name": result.name,
                    "nameLocal": result.name_local,
                    "province": result.province,
                    "category": result.category,
                    "tags": result.tags,
                    "rating": result.rating,
                    "reviewCount": result.review_count,
                    "image": result.image,
                    "description": result.description,
                    "confidence": result.confidence,
                    "matchedTerms": result.matched_terms,
                    "amenities": result.amenities,
                    "location": result.location,
                }
            )

        return jsonify(
            {
                "results": results_dict,
                "suggestions": [],  # Suggestions handled separately
                "totalCount": len(results_dict),
                "query": search_query.query,
                "processingTime": 0,  # Will be calculated in actual implementation
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/search/suggestions", methods=["POST"])
def search_suggestions():
    """Search suggestions endpoint"""
    try:
        data = request.get_json()

        search_query = SearchQuery(
            query=data.get("query", ""),
            language=data.get("language", "en"),
            filters=data.get("filters", {}),
        )

        _, suggestions = search_engine.search_places(search_query)

        # Convert suggestions to dictionaries
        suggestions_dict = []
        for suggestion in suggestions:
            suggestions_dict.append(
                {
                    "id": suggestion.id,
                    "type": suggestion.type,
                    "text": suggestion.text,
                    "description": suggestion.description,
                    "confidence": suggestion.confidence,
                    "province": suggestion.province,
                    "category": suggestion.category,
                    "image": suggestion.image,
                }
            )

        return jsonify({"suggestions": suggestions_dict})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/search/trending", methods=["GET"])
def get_trending_searches():
    """Get trending search terms"""
    language = request.args.get("language", "en")
    trending = {
        "th": ["เกาะพีพี", "วัดพระแก้ว", "ดอยอินทนนท์", "ตลาดน้ำ", "ชายหาด"],
        "en": [
            "Phi Phi Islands",
            "Wat Phra Kaew",
            "Doi Inthanon",
            "Floating Market",
            "Beach",
        ],
    }
    return jsonify({"trending": trending.get(language, trending["en"])})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
