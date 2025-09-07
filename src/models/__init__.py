from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .attraction import Attraction  # noqa
from .review import Review  # noqa
from .user import User  # noqa
from .room import Room  # noqa
from .car import Car  # noqa
from .room_booking import RoomBooking  # noqa
from .car_rental import CarRental  # noqa
from .video_post import VideoPost  # noqa
from .api_analytics import APIAnalytics  # noqa
from .external_data import DataSource, ManualUpdate, ScheduledUpdate  # noqa
from .project import Project  # noqa
from .task import Task  # noqa
from .post import Post, Like, Comment  # noqa

# HACK: Manually register the refactored 'Attraction' model's table with the
# legacy 'db' object's metadata.
# This is necessary because the tests use a Flask app context with db.create_all(),
# which only knows about metadata registered with this 'db' instance.
# The Attraction model was refactored to use a different Base for Alembic
# migrations, which removed it from this metadata. This line adds it back
# just for the test environment's table creation process.
Attraction.__table__.to_metadata(db.metadata)
