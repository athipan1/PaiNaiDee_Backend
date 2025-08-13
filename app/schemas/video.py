from marshmallow import Schema, fields, validate


class VideoUploadSchema(Schema):
    caption = fields.Str(validate=validate.Length(max=500))
    title = fields.Str(validate=validate.Length(max=255))


class VideoListSchema(Schema):
    id = fields.Int(required=True)
    user_id = fields.Int(required=True)
    username = fields.Str(required=True)
    title = fields.Str(required=True)
    description = fields.Str(allow_none=True)
    caption = fields.Str(allow_none=True)
    video_url = fields.Str(required=True)
    thumbnail_url = fields.Str(allow_none=True)
    duration = fields.Int(allow_none=True)
    file_size = fields.Int(allow_none=True)
    created_at = fields.Str(required=True)
    updated_at = fields.Str(allow_none=True)
