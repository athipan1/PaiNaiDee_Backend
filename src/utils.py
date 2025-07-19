from flask import jsonify, make_response

def standardized_response(data=None, message="", success=True, status_code=200):
    """
    Helper function to create a standardized JSON response.
    """
    response_data = {
        "success": success,
        "data": data,
        "message": message
    }
    response = make_response(jsonify(response_data), status_code)
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    return response
