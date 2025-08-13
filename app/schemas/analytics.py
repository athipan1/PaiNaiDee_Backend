from marshmallow import Schema, fields, validate


class EndpointSummarySchema(Schema):
    """Schema for endpoint summary data"""

    endpoint = fields.Str(required=True)
    method = fields.Str(required=True)
    request_count = fields.Int(required=True)
    avg_response_time = fields.Float(required=True)
    min_response_time = fields.Float(required=True)
    max_response_time = fields.Float(required=True)
    last_request = fields.DateTime(required=True, allow_none=True)


class RequestCountPeriodSchema(Schema):
    """Schema for request count by period data"""

    period = fields.Str(required=True)
    request_count = fields.Int(required=True)


class StatusCodeDistributionSchema(Schema):
    """Schema for status code distribution data"""

    status_code = fields.Int(required=True)
    count = fields.Int(required=True)
    percentage = fields.Float(required=True)


class SourceIPSchema(Schema):
    """Schema for source IP analytics"""

    source_ip = fields.Str(required=True)
    request_count = fields.Int(required=True)
    last_request = fields.DateTime(required=True, allow_none=True)


class ResponseTimeAnalyticsSchema(Schema):
    """Schema for response time analytics"""

    avg_response_time = fields.Float(required=True)
    min_response_time = fields.Float(required=True)
    max_response_time = fields.Float(required=True)
    median_response_time = fields.Float(required=True)
    p95_response_time = fields.Float(required=True)


class SystemOverviewSchema(Schema):
    """Schema for system overview analytics"""

    total_requests = fields.Int(required=True)
    unique_endpoints = fields.Int(required=True)
    unique_source_ips = fields.Int(required=True)
    error_rate = fields.Float(required=True)
    latest_request = fields.DateTime(required=True, allow_none=True)
    date_range = fields.Nested(
        {
            "start_date": fields.DateTime(required=True),
            "end_date": fields.DateTime(required=True),
        }
    )


class DashboardQuerySchema(Schema):
    """Schema for dashboard query parameters"""

    start_date = fields.DateTime(required=False, allow_none=True)
    end_date = fields.DateTime(required=False, allow_none=True)
    period = fields.Str(
        required=False, validate=validate.OneOf(["day", "week", "month"])
    )
    limit = fields.Int(required=False, validate=validate.Range(min=1, max=100))
