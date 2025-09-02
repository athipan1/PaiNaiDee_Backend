from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy import text, or_, and_, func
from src.models import db, Attraction, Review
import re
import unicodedata
from dataclasses import dataclass


@dataclass
class SearchQuery:
    """Search query parameters"""
    query: str = ""
    language: str = "th"
    province: Optional[str] = None
    category: Optional[str] = None
    min_rating: Optional[float] = None
    max_rating: Optional[float] = None
    amenities: Optional[List[str]] = None
    sort_by: str = "relevance"  # relevance, rating, name, distance
    limit: int = 20
    offset: int = 0


@dataclass
class SearchResult:
    """Search result item"""
    attraction: Attraction
    similarity_score: float
    matched_fields: List[str]


class SearchService:
    """Advanced search service with fuzzy search capabilities"""

    def __init__(self):
        """Initialize search service"""
        self.thai_synonyms = {
            "ทะเล": ["ชายหาด", "หาด", "เกาะ", "น้ำ"],
            "วัด": ["พระ", "โบสถ์", "ศาสนา", "พุทธ"],
            "ภูเขา": ["ดอย", "เขา", "ยอด", "ปีน"],
            "อาหาร": ["กิน", "ตลาด", "ร้านอาหาร", "รสชาติ"],
            "ธรรมชาติ": ["ป่า", "น้ำตก", "สวน", "สัตว์"],
            "ที่พัก": ["โรงแรม", "รีสอร์ท", "บ้านพัก", "นอน"],
            "เที่ยว": ["ท่องเที่ยว", "เดินทาง", "ไป", "เยี่ยม"],
        }

        self.english_synonyms = {
            "beach": ["sea", "ocean", "coast", "island", "water"],
            "temple": ["wat", "buddhist", "religious", "sacred", "buddha"],
            "mountain": ["hill", "peak", "summit", "doi", "climb"],
            "food": ["restaurant", "market", "cuisine", "dining", "taste"],
            "nature": ["forest", "waterfall", "park", "wildlife", "natural"],
            "accommodation": ["hotel", "resort", "homestay", "stay", "sleep"],
            "travel": ["tourism", "visit", "trip", "tour", "explore"],
        }

    def ensure_pg_trgm_extension(self) -> bool:
        """Ensure pg_trgm extension is available (for production use)"""
        try:
            # Check if running on SQLite (testing)
            if 'sqlite' in str(db.engine.url):
                return False
            
            # Try to enable pg_trgm extension
            db.session.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm;"))
            db.session.commit()
            return True
        except Exception:
            # Extension not available or not PostgreSQL
            return False

    def normalize_text(self, text: str) -> str:
        """Normalize text for better matching"""
        if not text:
            return ""
        
        # Convert to lowercase and remove diacritics
        text = unicodedata.normalize("NFD", text.lower())
        text = "".join(c for c in text if unicodedata.category(c) != "Mn")
        
        # Remove extra whitespace and special characters
        text = re.sub(r"[^\w\s]", " ", text)
        text = re.sub(r"\s+", " ", text.strip())
        return text

    def expand_query_with_synonyms(self, query: str, language: str) -> List[str]:
        """Expand query with synonyms"""
        if not query:
            return []
        
        expanded_terms = [query]
        query_lower = self.normalize_text(query)
        
        synonyms = self.thai_synonyms if language == "th" else self.english_synonyms
        
        # Find synonyms for query terms
        for key_term, synonym_list in synonyms.items():
            if key_term in query_lower:
                expanded_terms.extend(synonym_list)
            
            for synonym in synonym_list:
                if synonym in query_lower:
                    expanded_terms.append(key_term)
        
        return list(set(expanded_terms))

    def calculate_similarity_score(
        self, 
        query_terms: List[str], 
        attraction: Attraction, 
        use_pg_trgm: bool = False
    ) -> Tuple[float, List[str]]:
        """Calculate similarity score between query and attraction"""
        if not query_terms:
            return 0.0, []
        
        matched_fields = []
        scores = []
        
        # Fields to search with their weights
        search_fields = [
            ("name", attraction.name, 1.0),
            ("description", attraction.description, 0.8),
            ("province", attraction.province, 0.7),
            ("district", attraction.district, 0.6),
            ("category", attraction.category, 0.9),
            ("address", attraction.address, 0.5),
        ]
        
        for field_name, field_value, weight in search_fields:
            if not field_value:
                continue
                
            field_normalized = self.normalize_text(field_value)
            field_score = 0.0
            
            for term in query_terms:
                term_normalized = self.normalize_text(term)
                
                if not term_normalized:
                    continue
                
                # Exact match (highest score)
                if term_normalized == field_normalized:
                    field_score = max(field_score, 1.0)
                    matched_fields.append(f"{field_name}:exact")
                
                # Contains match
                elif term_normalized in field_normalized:
                    field_score = max(field_score, 0.8)
                    matched_fields.append(f"{field_name}:contains")
                
                # Word boundary match
                elif any(term_normalized in word for word in field_normalized.split()):
                    field_score = max(field_score, 0.6)
                    matched_fields.append(f"{field_name}:word")
                
                # Partial match (fuzzy)
                elif self._fuzzy_match(term_normalized, field_normalized) > 0.7:
                    field_score = max(field_score, 0.4)
                    matched_fields.append(f"{field_name}:fuzzy")
            
            if field_score > 0:
                scores.append(field_score * weight)
        
        # Calculate overall score
        if scores:
            overall_score = max(scores)  # Take the best matching field
        else:
            overall_score = 0.0
        
        return overall_score, list(set(matched_fields))

    def _fuzzy_match(self, term: str, text: str) -> float:
        """Simple fuzzy matching using character-based similarity"""
        if not term or not text:
            return 0.0
        
        # Simple Levenshtein-like similarity
        from difflib import SequenceMatcher
        return SequenceMatcher(None, term, text).ratio()

    def search_attractions_with_fuzzy(self, search_query: SearchQuery) -> Tuple[List[SearchResult], int]:
        """
        Perform fuzzy search on attractions with integrated review statistics to avoid N+1 queries.
        """
        use_pg_trgm = self.ensure_pg_trgm_extension()

        # Subquery for review stats, to be joined with the main query.
        review_stats_subquery = (
            db.session.query(
                Review.place_id,
                func.avg(Review.rating).label("average_rating"),
                func.count(Review.id).label("total_reviews"),
            )
            .group_by(Review.place_id)
            .subquery()
        )

        # Base query joining Attraction with review stats.
        query = db.session.query(
            Attraction,
            review_stats_subquery.c.average_rating,
            review_stats_subquery.c.total_reviews,
        ).outerjoin(
            review_stats_subquery,
            Attraction.id == review_stats_subquery.c.place_id,
        )

        # Apply standard filters.
        if search_query.province:
            query = query.filter(Attraction.province.ilike(f"%{search_query.province}%"))
        if search_query.category:
            query = query.filter(Attraction.category.ilike(f"%{search_query.category}%"))

        # Apply rating filters directly in the query.
        if search_query.min_rating is not None:
            query = query.filter(review_stats_subquery.c.average_rating >= search_query.min_rating)
        if search_query.max_rating is not None:
            query = query.filter(review_stats_subquery.c.average_rating <= search_query.max_rating)

        # The rest of the logic performs fuzzy matching on the pre-filtered results.
        # This is less efficient than a full DB solution but avoids a major refactor of fuzzy logic.
        
        initial_results = query.all()
        
        # This list will hold tuples of (Attraction, avg_rating, total_reviews)
        attraction_data_tuples = initial_results

        # Fuzzy search logic now operates on this pre-fetched and pre-filtered data.
        if search_query.query:
            expanded_terms = self.expand_query_with_synonyms(search_query.query, search_query.language)
            results_with_scores = []
            for attraction, avg_rating, total_reviews in attraction_data_tuples:
                similarity_score, matched_fields = self.calculate_similarity_score(
                    expanded_terms, attraction, use_pg_trgm
                )
                if similarity_score > 0.2:
                    # We create a temporary object to hold all data for sorting
                    temp_result = SearchResult(
                        attraction=attraction,
                        similarity_score=similarity_score,
                        matched_fields=matched_fields,
                    )
                    # Also attach stats for sorting
                    temp_result.average_rating = avg_rating if avg_rating else 0
                    temp_result.total_reviews = total_reviews if total_reviews else 0
                    results_with_scores.append(temp_result)
            
            results = results_with_scores
        else:
            # No query, just convert all results to SearchResult objects
            results = [
                SearchResult(
                    attraction=attraction,
                    similarity_score=1.0,
                    matched_fields=["all"],
                )
                for attraction, avg_rating, total_reviews in attraction_data_tuples
            ]
            # Attach stats for sorting
            for i, res in enumerate(results):
                _, avg_rating, total_reviews = attraction_data_tuples[i]
                res.average_rating = avg_rating if avg_rating else 0
                res.total_reviews = total_reviews if total_reviews else 0

        # Sort results using the pre-fetched stats.
        if search_query.sort_by == "relevance":
            results.sort(key=lambda x: x.similarity_score, reverse=True)
        elif search_query.sort_by == "rating":
            results.sort(key=lambda x: x.average_rating, reverse=True)
        elif search_query.sort_by == "name":
            results.sort(key=lambda x: x.attraction.name)

        total_count = len(results)
        
        # Apply pagination
        start_idx = search_query.offset
        end_idx = start_idx + search_query.limit
        paginated_results = results[start_idx:end_idx]

        # The route needs the full tuple for to_dict, so we reconstruct it.
        # However, the route was simplified to not need this. The `to_dict` in the route
        # now gets its data from the SearchResult object itself.
        # Let's adjust the route to use the SearchResult object correctly.
        # For now, the service returns this list of SearchResult objects.
        # The route will need to be adapted.

        # I will modify the route to pass the pre-calculated stats into to_dict.
        # The service will return a list of SearchResult objects, and I'll add the stats to them.

        return paginated_results, total_count

    def get_search_suggestions(
        self, 
        query: str, 
        language: str = "th", 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get search suggestions for autocomplete"""
        if not query or len(query) < 2:
            return []
        
        suggestions = []
        
        # Attraction name suggestions
        attractions = (
            db.session.query(Attraction)
            .filter(Attraction.name.ilike(f"%{query}%"))
            .limit(limit // 2)
            .all()
        )
        
        for attraction in attractions:
            suggestions.append({
                "id": f"attraction-{attraction.id}",
                "type": "attraction",
                "text": attraction.name,
                "description": attraction.province,
                "confidence": 1.0,
                "province": attraction.province,
                "category": attraction.category,
                "image": attraction.main_image_url,
            })
        
        # Province suggestions
        provinces = (
            db.session.query(Attraction.province)
            .filter(Attraction.province.ilike(f"%{query}%"))
            .distinct()
            .limit(3)
            .all()
        )
        
        for province_tuple in provinces:
            province = province_tuple[0]
            if province:
                suggestions.append({
                    "id": f"province-{province.lower().replace(' ', '-')}",
                    "type": "province",
                    "text": province,
                    "description": "จังหวัด" if language == "th" else "Province",
                    "confidence": 0.8,
                })
        
        # Category suggestions
        categories = (
            db.session.query(Attraction.category)
            .filter(Attraction.category.ilike(f"%{query}%"))
            .distinct()
            .limit(3)
            .all()
        )
        
        for category_tuple in categories:
            category = category_tuple[0]
            if category:
                suggestions.append({
                    "id": f"category-{category.lower().replace(' ', '-')}",
                    "type": "category",
                    "text": category,
                    "description": "หมวดหมู่" if language == "th" else "Category",
                    "confidence": 0.7,
                })
        
        return suggestions[:limit]

    def get_trending_searches(self, language: str = "th") -> List[str]:
        """Get trending search terms"""
        trending = {
            "th": ["ทะเล", "วัด", "ภูเขา", "น้ำตก", "ตลาด", "เกาะ", "ชายหาด"],
            "en": ["beach", "temple", "mountain", "waterfall", "market", "island", "coast"],
        }
        return trending.get(language, trending["th"])