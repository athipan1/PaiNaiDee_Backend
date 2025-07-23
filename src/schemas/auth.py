from marshmallow import Schema, fields, validate


class RegisterSchema(Schema):
    username = fields.Str(
        required=True, validate=validate.Length(min=3, max=80)
    )
    password = fields.Str(
        required=True, validate=validate.Length(min=6, max=200)
    )


class LoginSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)
