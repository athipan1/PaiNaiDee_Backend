from marshmallow import Schema, fields


class RoomBookingSchema(Schema):
    room_id = fields.Int(required=True)
    date_start = fields.Date(required=True)
    date_end = fields.Date(required=True)


class CarRentalSchema(Schema):
    car_id = fields.Int(required=True)
    date_start = fields.Date(required=True)
    date_end = fields.Date(required=True)
