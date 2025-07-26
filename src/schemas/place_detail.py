from marshmallow import Schema, fields, validate


class PlaceDetailSchema(Schema):
    description = fields.Str(required=False, allow_none=True)
    link = fields.Str(required=False, allow_none=True, validate=validate.Length(max=255))


class PlaceDetailResponseSchema(Schema):
    id = fields.Int()
    place_id = fields.Int()
    description = fields.Str()
    link = fields.Str()