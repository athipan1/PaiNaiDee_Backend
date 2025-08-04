from marshmallow import Schema, fields, validate


class RegisterSchema(Schema):
    username = fields.Str(
        required=True, validate=validate.Length(min=3, max=80)
    )
    email = fields.Email(required=True)
    password = fields.Str(
        required=True, validate=validate.Length(min=6, max=200)
    )


class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)


class AdminRegisterSchema(Schema):
    username = fields.Str(
        required=True, validate=validate.Length(min=3, max=80)
    )
    email = fields.Email(required=True)
    password = fields.Str(
        required=True, validate=validate.Length(min=8, max=200)
    )


class AdminLoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)
