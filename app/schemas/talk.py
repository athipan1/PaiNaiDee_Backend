from marshmallow import Schema, fields, validate


class TalkRequestSchema(Schema):
    sender = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    receiver = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    message = fields.Str(required=True, validate=validate.Length(min=1, max=2000))
    session_id = fields.Str(
        validate=validate.Length(max=100)
    )  # Optional for session management


class TalkResponseSchema(Schema):
    reply = fields.Str(required=True)
    session_id = fields.Str()  # Include session_id in response if provided
