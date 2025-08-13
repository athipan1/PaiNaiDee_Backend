from marshmallow import Schema, fields, validate


class ReviewSchema(Schema):
    place_id = fields.Int(required=True)
    rating = fields.Int(required=True, validate=validate.Range(min=1, max=5))
    comment = fields.Str(validate=validate.Length(max=500))
