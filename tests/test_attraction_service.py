import pytest
from src.models import db, Attraction, Review
from src.services.attraction_service import AttractionService

@pytest.fixture
def setup_attractions_and_reviews(app):
    with app.app_context():
        # Attraction 1: 2 reviews
        attraction1 = Attraction(name="Beach", province="South", category="Nature")
        db.session.add(attraction1)
        db.session.commit()
        review1_1 = Review(place_id=attraction1.id, user_id=1, rating=5, comment="Amazing!")
        review1_2 = Review(place_id=attraction1.id, user_id=2, rating=3, comment="Okay")

        # Attraction 2: 1 review
        attraction2 = Attraction(name="Mountain", province="North", category="Adventure")
        db.session.add(attraction2)
        db.session.commit()
        review2_1 = Review(place_id=attraction2.id, user_id=1, rating=4, comment="Great view")

        # Attraction 3: No reviews
        attraction3 = Attraction(name="Museum", province="Central", category="Culture")

        db.session.add_all([review1_1, review1_2, review2_1, attraction3])
        db.session.commit()

        yield {
            "attraction1_id": attraction1.id,
            "attraction2_id": attraction2.id,
            "attraction3_id": attraction3.id
        }

        # Teardown
        db.session.query(Review).delete()
        db.session.query(Attraction).delete()
        db.session.commit()

def test_get_all_attractions_with_reviews(app, setup_attractions_and_reviews):
    with app.app_context():
        # Call the service to get all attractions
        paginated_results = AttractionService.get_all_attractions(page=1, limit=10, q=None, province=None, category=None)

        assert paginated_results.total == 3

        results = {item[0].id: item for item in paginated_results.items}

        # Attraction 1: Avg rating (5+3)/2 = 4.0, 2 reviews
        attraction1_id = setup_attractions_and_reviews["attraction1_id"]
        assert attraction1_id in results
        attraction1_obj, avg_rating1, total_reviews1 = results[attraction1_id]
        assert attraction1_obj.name == "Beach"
        assert avg_rating1 == 4.0
        assert total_reviews1 == 2

        # Attraction 2: Avg rating 4.0, 1 review
        attraction2_id = setup_attractions_and_reviews["attraction2_id"]
        assert attraction2_id in results
        attraction2_obj, avg_rating2, total_reviews2 = results[attraction2_id]
        assert attraction2_obj.name == "Mountain"
        assert avg_rating2 == 4.0
        assert total_reviews2 == 1

        # Attraction 3: No reviews, should have None for stats from query
        attraction3_id = setup_attractions_and_reviews["attraction3_id"]
        assert attraction3_id in results
        attraction3_obj, avg_rating3, total_reviews3 = results[attraction3_id]
        assert attraction3_obj.name == "Museum"
        assert avg_rating3 is None
        assert total_reviews3 is None
