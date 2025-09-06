from src.models import db, User

class UserService:
    @staticmethod
    def follow_user(follower_id: int, followed_id: int):
        """
        Makes a user (follower_id) follow another user (followed_id).
        Returns a tuple of (success, message).
        """
        if follower_id == followed_id:
            return False, "You cannot follow yourself."

        follower = db.session.get(User, follower_id)
        followed = db.session.get(User, followed_id)

        if not follower or not followed:
            return False, "One or both users not found."

        if follower.followed.filter_by(id=followed_id).count() > 0:
            return False, "You are already following this user."

        follower.followed.append(followed)
        db.session.commit()
        return True, f"You are now following {followed.username}."

    @staticmethod
    def unfollow_user(follower_id: int, followed_id: int):
        """
        Makes a user (follower_id) unfollow another user (followed_id).
        Returns a tuple of (success, message).
        """
        follower = db.session.get(User, follower_id)
        followed = db.session.get(User, followed_id)

        if not follower or not followed:
            return False, "One or both users not found."

        if follower.followed.filter_by(id=followed_id).count() == 0:
            return False, "You are not following this user."

        follower.followed.remove(followed)
        db.session.commit()
        return True, f"You have unfollowed {followed.username}."

    @staticmethod
    def is_following(follower_id: int, followed_id: int) -> bool:
        """Checks if a user is following another user."""
        follower = db.session.get(User, follower_id)
        if not follower:
            return False
        return follower.followed.filter_by(id=followed_id).count() > 0
