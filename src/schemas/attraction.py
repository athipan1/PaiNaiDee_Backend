from marshmallow import Schema, fields, validate


class AttractionSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=3, max=255))
    description = fields.Str(required=True)
    province = fields.Str(required=True)
    district = fields.Str()
    latitude = fields.Float()
    longitude = fields.Float()
    category = fields.Str(required=True)
    opening_hours = fields.Str()
    entrance_fee = fields.Str()
    contact_phone = fields.Str()
    website = fields.Str()
    image_urls = fields.List(fields.Str())
