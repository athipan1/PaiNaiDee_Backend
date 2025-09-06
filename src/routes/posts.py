from flask import Blueprint, request, abort
from flask_jwt_extended import jwt_required, get_current_user
from src.services.post_service import PostService
from src.utils.response import standardized_response
from marshmallow import Schema, fields, ValidationError

posts_bp = Blueprint("posts", __name__)

class PostSchema(Schema):
    content = fields.Str(required=True)

class CommentSchema(Schema):
    content = fields.Str(required=True)

@posts_bp.route("/posts", methods=["GET"])
def get_posts_feed():
    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 10, type=int)

    paginated_posts, message = PostService.get_all_posts(page, limit)

    if paginated_posts is None:
        abort(500, description=message)

    results = [post.to_dict() for post in paginated_posts.items]

    pagination_data = {
        "total_pages": paginated_posts.pages,
        "current_page": paginated_posts.page,
        "total_items": paginated_posts.total,
        "has_next": paginated_posts.has_next,
        "has_prev": paginated_posts.has_prev,
    }

    return standardized_response(data={"posts": results, "pagination": pagination_data}, message=message)

@posts_bp.route("/posts", methods=["POST"])
@jwt_required()
def create_new_post():
    current_user = get_current_user()
    if not current_user:
        abort(401, description="Authentication required")

    try:
        validated_data = PostSchema().load(request.get_json())
    except ValidationError as err:
        return standardized_response(data=err.messages, success=False, status_code=400)

    content = validated_data["content"]

    new_post, message = PostService.create_post(user_id=current_user.id, content=content)

    if not new_post:
        abort(500, description=message)

    return standardized_response(data=new_post.to_dict(), message=message, status_code=201)

@posts_bp.route("/posts/<int:postId>/like", methods=["POST"])
@jwt_required()
def like_post(postId):
    current_user = get_current_user()
    if not current_user:
        abort(401, description="Authentication required")

    result, message = PostService.toggle_like(user_id=current_user.id, post_id=postId)

    if result is None:
        abort(404, description=message) # Assuming 404 for post not found

    return standardized_response(data=result, message=message)

@posts_bp.route("/posts/<int:postId>/engagement", methods=["GET"])
def get_post_engagement(postId):
    stats, message = PostService.get_engagement_stats(post_id=postId)

    if stats is None:
        abort(404, description=message)

    return standardized_response(data=stats, message=message)

@posts_bp.route("/posts/<int:postId>/comments", methods=["POST"])
@jwt_required()
def add_post_comment(postId):
    current_user = get_current_user()
    if not current_user:
        abort(401, description="Authentication required")

    try:
        validated_data = CommentSchema().load(request.get_json())
    except ValidationError as err:
        return standardized_response(data=err.messages, success=False, status_code=400)

    content = validated_data["content"]

    new_comment, message = PostService.add_comment(user_id=current_user.id, post_id=postId, content=content)

    if not new_comment:
        abort(404, description=message) # Assuming 404 for post not found

    return standardized_response(data=new_comment.to_dict(), message=message, status_code=201)

@posts_bp.route("/posts/<int:postId>/comments", methods=["GET"])
def get_post_comments(postId):
    comments, message = PostService.get_comments(post_id=postId)

    if comments is None:
        abort(404, description=message)

    return standardized_response(data=[comment.to_dict() for comment in comments], message=message)
