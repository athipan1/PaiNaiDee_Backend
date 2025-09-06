from src.models import db, Attraction

def test_autocomplete_locations(client, app):
    """Test the location autocomplete endpoint."""
    with app.app_context():
        # Add test attractions
        attraction1 = Attraction(name="Eiffel Tower", province="Paris")
        attraction2 = Attraction(name="Louvre Museum", province="Paris")
        attraction3 = Attraction(name="Big Ben", province="London")
        db.session.add_all([attraction1, attraction2, attraction3])
        db.session.commit()

    # Test query that should match two attractions
    rv = client.get("/api/locations/autocomplete?q=Paris")
    assert rv.status_code == 200
    json_data = rv.get_json()
    assert json_data["success"] is True
    data = json_data["data"]
    assert len(data) == 2
    names = {item["name"] for item in data}
    assert "Eiffel Tower" in names
    assert "Louvre Museum" in names

    # Test query that should match one attraction
    rv = client.get("/api/locations/autocomplete?q=London")
    assert rv.status_code == 200
    json_data = rv.get_json()
    assert json_data["success"] is True
    data = json_data["data"]
    assert len(data) == 1
    assert data[0]["name"] == "Big Ben"
    assert data[0]["country"] == "London" # Check that province is mapped to country

    # Test query with no matches
    rv = client.get("/api/locations/autocomplete?q=Tokyo")
    assert rv.status_code == 200
    json_data = rv.get_json()
    assert json_data["success"] is True
    assert len(json_data["data"]) == 0

    # Test query with partial match
    rv = client.get("/api/locations/autocomplete?q=eiffel")
    assert rv.status_code == 200
    json_data = rv.get_json()
    assert json_data["success"] is True
    assert len(json_data["data"]) == 1
    assert json_data["data"][0]["name"] == "Eiffel Tower"
