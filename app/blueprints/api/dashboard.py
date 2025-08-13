from datetime import datetime, timedelta
from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError
from ...services.analytics_service import AnalyticsService
from ...schemas.analytics import (
    DashboardQuerySchema,
    EndpointSummarySchema,
    RequestCountPeriodSchema,
    StatusCodeDistributionSchema,
    SourceIPSchema,
    ResponseTimeAnalyticsSchema,
    SystemOverviewSchema
)
from ...utils.response import standardized_response

dashboard_bp = Blueprint("dashboard", __name__)


def parse_query_params():
    """Parse and validate common query parameters"""
    query_schema = DashboardQuerySchema()
    try:
        query_params = {}
        
        # Parse datetime strings
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        if start_date_str:
            try:
                query_params['start_date'] = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
            except ValueError:
                return None, f"Invalid start_date format: {start_date_str}"
        
        if end_date_str:
            try:
                query_params['end_date'] = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
            except ValueError:
                return None, f"Invalid end_date format: {end_date_str}"
        
        # Validate period parameter
        period = request.args.get('period', 'day')
        if period not in ['day', 'week', 'month']:
            return None, f"Invalid period '{period}'. Must be one of: day, week, month"
        query_params['period'] = period
        
        query_params['limit'] = request.args.get('limit', 10, type=int)
        
        # Just return the params without schema validation for now to simplify
        return {k: v for k, v in query_params.items() if v is not None}
        
    except Exception as e:
        return None, str(e)


@dashboard_bp.route("/dashboard/overview", methods=["GET"])
@jwt_required()
def get_system_overview():
    """Get overall system analytics overview"""
    params_result = parse_query_params()
    if isinstance(params_result, tuple):
        return standardized_response(
            success=False,
            message=f"Invalid query parameters: {params_result[1]}",
            status_code=400
        )
    
    params = params_result
    
    try:
        overview_data = AnalyticsService.get_system_overview(
            start_date=params.get('start_date'),
            end_date=params.get('end_date')
        )
        
        # Skip schema validation for now and return data directly
        return standardized_response(
            data=overview_data,
            message="System overview retrieved successfully"
        )
    except Exception as e:
        return standardized_response(
            success=False,
            message=f"Error retrieving system overview: {str(e)}",
            status_code=500
        )


@dashboard_bp.route("/dashboard/endpoints", methods=["GET"])
@jwt_required()
def get_endpoints_summary():
    """Get summary statistics for all endpoints"""
    params_result = parse_query_params()
    if isinstance(params_result, tuple):
        return standardized_response(
            success=False,
            message=f"Invalid query parameters: {params_result[1]}",
            status_code=400
        )
    
    params = params_result
    
    try:
        endpoints_data = AnalyticsService.get_endpoint_summary(
            start_date=params.get('start_date'),
            end_date=params.get('end_date')
        )
        
        return standardized_response(
            data=endpoints_data,
            message="Endpoints summary retrieved successfully"
        )
    except Exception as e:
        return standardized_response(
            success=False,
            message=f"Error retrieving endpoints summary: {str(e)}",
            status_code=500
        )


@dashboard_bp.route("/dashboard/requests-by-period", methods=["GET"])
@jwt_required()
def get_requests_by_period():
    """Get request count grouped by time period"""
    params_result = parse_query_params()
    if isinstance(params_result, tuple):
        return standardized_response(
            success=False,
            message=f"Invalid query parameters: {params_result[1]}",
            status_code=400
        )
    
    params = params_result
    
    try:
        period_data = AnalyticsService.get_request_count_by_period(
            period=params.get('period', 'day'),
            start_date=params.get('start_date'),
            end_date=params.get('end_date')
        )
        
        return standardized_response(
            data=period_data,
            message="Request count by period retrieved successfully"
        )
    except Exception as e:
        return standardized_response(
            success=False,
            message=f"Error retrieving request count by period: {str(e)}",
            status_code=500
        )


@dashboard_bp.route("/dashboard/status-codes", methods=["GET"])
@jwt_required()
def get_status_code_distribution():
    """Get distribution of HTTP status codes"""
    params_result = parse_query_params()
    if isinstance(params_result, tuple):
        return standardized_response(
            success=False,
            message=f"Invalid query parameters: {params_result[1]}",
            status_code=400
        )
    
    params = params_result
    
    try:
        status_data = AnalyticsService.get_status_code_distribution(
            start_date=params.get('start_date'),
            end_date=params.get('end_date')
        )
        
        return standardized_response(
            data=status_data,
            message="Status code distribution retrieved successfully"
        )
    except Exception as e:
        return standardized_response(
            success=False,
            message=f"Error retrieving status code distribution: {str(e)}",
            status_code=500
        )


@dashboard_bp.route("/dashboard/source-ips", methods=["GET"])
@jwt_required()
def get_top_source_ips():
    """Get top source IPs by request count"""
    params_result = parse_query_params()
    if isinstance(params_result, tuple):
        return standardized_response(
            success=False,
            message=f"Invalid query parameters: {params_result[1]}",
            status_code=400
        )
    
    params = params_result
    
    try:
        ip_data = AnalyticsService.get_top_source_ips(
            limit=params.get('limit', 10),
            start_date=params.get('start_date'),
            end_date=params.get('end_date')
        )
        
        return standardized_response(
            data=ip_data,
            message="Top source IPs retrieved successfully"
        )
    except Exception as e:
        return standardized_response(
            success=False,
            message=f"Error retrieving top source IPs: {str(e)}",
            status_code=500
        )


@dashboard_bp.route("/dashboard/response-times", methods=["GET"])
@jwt_required()
def get_response_time_analytics():
    """Get response time analytics"""
    params_result = parse_query_params()
    if isinstance(params_result, tuple):
        return standardized_response(
            success=False,
            message=f"Invalid query parameters: {params_result[1]}",
            status_code=400
        )
    
    params = params_result
    
    try:
        response_time_data = AnalyticsService.get_response_time_analytics(
            start_date=params.get('start_date'),
            end_date=params.get('end_date')
        )
        
        return standardized_response(
            data=response_time_data,
            message="Response time analytics retrieved successfully"
        )
    except Exception as e:
        return standardized_response(
            success=False,
            message=f"Error retrieving response time analytics: {str(e)}",
            status_code=500
        )