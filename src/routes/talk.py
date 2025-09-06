from flask import Blueprint, request, jsonify
from src.services.talk_service import TalkService
from src.utils.response import standardized_response
from src.schemas.talk import TalkRequestSchema, TalkResponseSchema
from marshmallow import ValidationError

talk_bp = Blueprint("talk", __name__)
talk_service = TalkService()


@talk_bp.route("/predict", methods=["POST"])
def predict():
    """
    Simplified conversational AI endpoint.
    Accepts JSON: {"message": "..."}
    Returns JSON: {"reply": "..."}
    """
    try:
        data = request.get_json()
        if not data or "message" not in data:
            return standardized_response(
                message="Validation error: 'message' is required.",
                success=False,
                status_code=400
            )

        message = data["message"]

        # Use the talk service to generate a response
        # We can use default values for sender, receiver, and a new session_id for each predict call
        result = talk_service.generate_response(
            sender="user",
            receiver="PaiNaiDeeAI",
            message=message,
            session_id=None  # Or generate a temporary one
        )

        if not isinstance(result, dict) or 'reply' not in result:
            return standardized_response(
                message="Invalid response from talk service",
                success=False,
                status_code=500
            )

        return standardized_response(
            message="Response generated successfully",
            data={"reply": result["reply"]}
        )

    except Exception as e:
        return standardized_response(
            message="Failed to generate response",
            data={"error": str(e)},
            success=False,
            status_code=500
        )


@talk_bp.route("/talk", methods=["POST"])
def talk():
    """
    Conversational AI endpoint for program-to-program communication.
    
    Accepts JSON: {"sender": "A", "receiver": "B", "message": "...", "session_id": "..."}
    Returns JSON: {"reply": "...", "session_id": "..."}
    """
    try:
        # Validate request data
        schema = TalkRequestSchema()
        data = schema.load(request.json or {})
        
        # Extract parameters
        sender = data['sender']
        receiver = data['receiver']
        message = data['message']
        session_id = data.get('session_id')
        
        # Generate response using the talk service
        result = talk_service.generate_response(
            sender=sender,
            receiver=receiver,
            message=message,
            session_id=session_id
        )
        
        # Ensure the response has the expected structure
        if not isinstance(result, dict) or 'reply' not in result:
            response = jsonify({
                "success": False,
                "message": "Invalid response from talk service",
                "data": None
            })
            response.status_code = 500
            return response
        
        return standardized_response(
            message="Response generated successfully",
            data=result
        )
        
    except ValidationError as e:
        response = jsonify({
            "success": False,
            "message": "Validation error",
            "data": {"errors": e.messages}
        })
        response.status_code = 400
        return response
    
    except Exception as e:
        response = jsonify({
            "success": False,
            "message": "Failed to generate response",
            "data": {"error": str(e)}
        })
        response.status_code = 500
        return response


@talk_bp.route("/talk/session/<session_id>", methods=["GET"])
def get_session_info(session_id):
    """Get information about a conversation session."""
    try:
        session_info = talk_service.get_session_info(session_id)
        return standardized_response(
            message="Session information retrieved",
            data=session_info
        )
    except Exception as e:
        response = jsonify({
            "success": False,
            "message": "Failed to get session information",
            "data": {"error": str(e)}
        })
        response.status_code = 500
        return response


@talk_bp.route("/talk/session/<session_id>", methods=["DELETE"])
def clear_session(session_id):
    """Clear a conversation session."""
    try:
        success = talk_service.clear_session(session_id)
        if success:
            return standardized_response(
                message="Session cleared successfully"
            )
        else:
            response = jsonify({
                "success": False,
                "message": "Session not found",
                "data": None
            })
            response.status_code = 404
            return response
    except Exception as e:
        response = jsonify({
            "success": False,
            "message": "Failed to clear session",
            "data": {"error": str(e)}
        })
        response.status_code = 500
        return response


@talk_bp.route("/talk/roles", methods=["GET"])
def get_available_roles():
    """Get available role configurations."""
    try:
        roles = talk_service.DEFAULT_ROLES
        return standardized_response(
            message="Available roles retrieved",
            data={"roles": roles}
        )
    except Exception as e:
        response = jsonify({
            "success": False,
            "message": "Failed to get roles",
            "data": {"error": str(e)}
        })
        response.status_code = 500
        return response