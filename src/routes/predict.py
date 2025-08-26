from flask import Blueprint, request
from src.utils.response import standardized_response

predict_bp = Blueprint("predict", __name__)


@predict_bp.route("/predict", methods=["POST"])
def predict():
    """
    Endpoint to receive user preferences and return travel predictions.
    This is a placeholder implementation.
    """
    data = request.get_json()
    if not data:
        return standardized_response(
            message="Invalid input: No data provided.", success=False, status_code=400
        )

    # In the future, this will process the data and return actual predictions.
    # For now, it just echoes the received data.
    response_data = {
        "message": "Prediction endpoint called successfully.",
        "received_data": data,
    }

    return standardized_response(data=response_data)
