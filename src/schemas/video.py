from marshmallow import Schema, fields, validate


class VideoUploadSchema(Schema):
    caption = fields.Str(validate=validate.Length(max=500))


class VideoListSchema(Schema):
    id = fields.Int(required=True)
    user_id = fields.Int(required=True)
    username = fields.Str(required=True)
    caption = fields.Str(allow_none=True)
    video_url = fields.Str(required=True)
    created_at = fields.Str(required=True)