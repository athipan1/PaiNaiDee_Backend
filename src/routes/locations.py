from flask import Blueprint, request
from src.services.search_service import SearchService
from src.utils.response import standardized_response

locations_bp = Blueprint("locations", __name__)
search_service = SearchService()

@locations_bp.route("/autocomplete", methods=["GET"])
def autocomplete_locations():
    """
    Provides autocomplete suggestions for locations.
    """
    query = request.args.get("q", "")
    if not query:
        return standardized_response(data=[], message="Query parameter 'q' is required.")

    try:
        locations = search_service.autocomplete_locations(query)
        return standardized_response(data=locations)
    except Exception as e:
        return standardized_response(
            message=f"An error occurred: {str(e)}",
            success=False,
            status_code=500
        )
