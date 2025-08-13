from flask import jsonify


def standardized_response(data=None, message="", success=True, status_code=200):
    response = {"success": success, "data": data, "message": message}
    return jsonify(response), status_code
