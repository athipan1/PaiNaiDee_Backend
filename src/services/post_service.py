from src.models import db, Post, User, Like, Comment
from sqlalchemy.exc import SQLAlchemyError

class PostService:
    @staticmethod
    def create_post(user_id, content):
        try:
            user = User.query.get(user_id)
            if not user:
                return None, "User not found"

            new_post = Post(user_id=user_id, content=content)
            db.session.add(new_post)
            db.session.commit()
            return new_post, "Post created successfully"
        except SQLAlchemyError as e:
            db.session.rollback()
            return None, str(e)

    @staticmethod
    def get_all_posts(page=1, limit=10):
        try:
            paginated_posts = Post.query.order_by(Post.created_at.desc()).paginate(page=page, per_page=limit, error_out=False)
            return paginated_posts, "Posts retrieved successfully"
        except SQLAlchemyError as e:
            return None, str(e)

    @staticmethod
    def get_post_by_id(post_id):
        try:
            post = Post.query.get(post_id)
            if not post:
                return None, "Post not found"
            return post, "Post retrieved successfully"
        except SQLAlchemyError as e:
            return None, str(e)

    @staticmethod
    def toggle_like(user_id, post_id):
        try:
            post = Post.query.get(post_id)
            if not post:
                return None, "Post not found"

            like = Like.query.filter_by(user_id=user_id, post_id=post_id).first()

            if like:
                # User has already liked the post, so unlike it
                db.session.delete(like)
                db.session.commit()
                return {"liked": False, "likes_count": post.likes.count()}, "Post unliked successfully"
            else:
                # User has not liked the post, so like it
                new_like = Like(user_id=user_id, post_id=post_id)
                db.session.add(new_like)
                db.session.commit()
                return {"liked": True, "likes_count": post.likes.count()}, "Post liked successfully"
        except SQLAlchemyError as e:
            db.session.rollback()
            return None, str(e)

    @staticmethod
    def add_comment(user_id, post_id, content):
        try:
            post = Post.query.get(post_id)
            if not post:
                return None, "Post not found"

            new_comment = Comment(user_id=user_id, post_id=post_id, content=content)
            db.session.add(new_comment)
            db.session.commit()
            return new_comment, "Comment added successfully"
        except SQLAlchemyError as e:
            db.session.rollback()
            return None, str(e)

    @staticmethod
    def get_comments(post_id):
        try:
            post = Post.query.get(post_id)
            if not post:
                return None, "Post not found"

            comments = Comment.query.filter_by(post_id=post_id).order_by(Comment.created_at.asc()).all()
            return comments, "Comments retrieved successfully"
        except SQLAlchemyError as e:
            return None, str(e)

    @staticmethod
    def get_engagement_stats(post_id):
        try:
            post = Post.query.get(post_id)
            if not post:
                return None, "Post not found"

            stats = {
                "likes_count": post.likes.count(),
                "comments_count": post.comments.count()
            }
            return stats, "Engagement stats retrieved successfully"
        except SQLAlchemyError as e:
            return None, str(e)
