from werkzeug.exceptions import HTTPException
from .utils.response import standardized_response


def register_error_handlers(app):
    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        return standardized_response(
            message=e.description, success=False, status_code=e.code
        )

    @app.errorhandler(Exception)
    def handle_generic_exception(e):
        # For production, you might want to log the error
        # import traceback
        # traceback.print_exc()
        return standardized_response(
            message="An unexpected error occurred.",
            success=False,
            status_code=500,
        )
