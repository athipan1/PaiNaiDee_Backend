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
from .place_detail import PlaceDetail  # noqa
