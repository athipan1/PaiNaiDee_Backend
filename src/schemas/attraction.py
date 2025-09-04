from marshmallow import Schema, fields, validate


class AttractionSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=3, max=255))
    description = fields.Str(required=True)
    location = fields.Str()
    province = fields.Str(required=True)
    district = fields.Str()
    address = fields.Str()
