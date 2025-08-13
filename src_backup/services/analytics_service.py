from datetime import datetime, timedelta
from sqlalchemy import func, desc, distinct
from src.models import db
from src.models.api_analytics import APIAnalytics


class AnalyticsService:
    """Service for retrieving and processing API analytics data"""
    
    @staticmethod
    def get_endpoint_summary(start_date=None, end_date=None):
        """Get summary statistics for all endpoints"""
        query = db.session.query(
            APIAnalytics.endpoint,
            APIAnalytics.method,
            func.count(APIAnalytics.id).label('request_count'),
            func.avg(APIAnalytics.response_time).label('avg_response_time'),
            func.min(APIAnalytics.response_time).label('min_response_time'),
            func.max(APIAnalytics.response_time).label('max_response_time'),
            func.max(APIAnalytics.timestamp).label('last_request')
        )
        
        if start_date:
            query = query.filter(APIAnalytics.timestamp >= start_date)
        if end_date:
            query = query.filter(APIAnalytics.timestamp <= end_date)
        
        query = query.group_by(APIAnalytics.endpoint, APIAnalytics.method)
        query = query.order_by(desc('request_count'))
        
        results = query.all()
        
        return [
            {
                'endpoint': result.endpoint,
                'method': result.method,
                'request_count': result.request_count,
                'avg_response_time': round(result.avg_response_time, 2) if result.avg_response_time else 0,
                'min_response_time': round(result.min_response_time, 2) if result.min_response_time else 0,
                'max_response_time': round(result.max_response_time, 2) if result.max_response_time else 0,
                'last_request': result.last_request.isoformat() if result.last_request else None
            }
            for result in results
        ]
    
    @staticmethod
    def get_request_count_by_period(period='day', start_date=None, end_date=None):
        """Get request count grouped by time period (day/week/month)"""
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()
        
        # Use database-agnostic date formatting
        if period == 'day':
            date_format = func.date(APIAnalytics.timestamp)
        elif period == 'week':
            # For SQLite compatibility, use a simpler approach
            date_format = func.strftime('%Y-%W', APIAnalytics.timestamp)
        elif period == 'month':
            # For SQLite compatibility, use a simpler approach  
            date_format = func.strftime('%Y-%m', APIAnalytics.timestamp)
        else:
            date_format = func.date(APIAnalytics.timestamp)
        
        query = db.session.query(
            date_format.label('period'),
            func.count(APIAnalytics.id).label('request_count')
        ).filter(
            APIAnalytics.timestamp >= start_date,
            APIAnalytics.timestamp <= end_date
        ).group_by(date_format).order_by(date_format)
        
        results = query.all()
        
        return [
            {
                'period': str(result.period),
                'request_count': result.request_count
            }
            for result in results
        ]
    
    @staticmethod
    def get_status_code_distribution(start_date=None, end_date=None):
        """Get distribution of HTTP status codes"""
        query = db.session.query(
            APIAnalytics.status_code,
            func.count(APIAnalytics.id).label('count')
        )
        
        if start_date:
            query = query.filter(APIAnalytics.timestamp >= start_date)
        if end_date:
            query = query.filter(APIAnalytics.timestamp <= end_date)
        
        query = query.group_by(APIAnalytics.status_code)
        query = query.order_by(desc('count'))
        
        results = query.all()
        
        # Calculate total for percentage
        total_count = sum(r.count for r in results)
        
        return [
            {
                'status_code': result.status_code,
                'count': result.count,
                'percentage': round((result.count / total_count) * 100, 2) if total_count > 0 else 0
            }
            for result in results
        ]
    
    @staticmethod
    def get_top_source_ips(limit=10, start_date=None, end_date=None):
        """Get top source IPs by request count"""
        query = db.session.query(
            APIAnalytics.source_ip,
            func.count(APIAnalytics.id).label('request_count'),
            func.max(APIAnalytics.timestamp).label('last_request')
        ).filter(APIAnalytics.source_ip.isnot(None))
        
        if start_date:
            query = query.filter(APIAnalytics.timestamp >= start_date)
        if end_date:
            query = query.filter(APIAnalytics.timestamp <= end_date)
        
        query = query.group_by(APIAnalytics.source_ip)
        query = query.order_by(desc('request_count'))
        query = query.limit(limit)
        
        results = query.all()
        
        return [
            {
                'source_ip': result.source_ip,
                'request_count': result.request_count,
                'last_request': result.last_request.isoformat() if result.last_request else None
            }
            for result in results
        ]
    
    @staticmethod
    def get_response_time_analytics(start_date=None, end_date=None):
        """Get overall response time analytics"""
        query = db.session.query(
            func.avg(APIAnalytics.response_time).label('avg_response_time'),
            func.min(APIAnalytics.response_time).label('min_response_time'),
            func.max(APIAnalytics.response_time).label('max_response_time')
        )
        
        if start_date:
            query = query.filter(APIAnalytics.timestamp >= start_date)
        if end_date:
            query = query.filter(APIAnalytics.timestamp <= end_date)
        
        result = query.first()
        
        # For median and p95, we'll calculate them separately for database compatibility
        median_query = db.session.query(APIAnalytics.response_time)
        if start_date:
            median_query = median_query.filter(APIAnalytics.timestamp >= start_date)
        if end_date:
            median_query = median_query.filter(APIAnalytics.timestamp <= end_date)
        
        response_times = [r[0] for r in median_query.all()]
        response_times.sort()
        
        median_response_time = 0
        p95_response_time = 0
        
        if response_times:
            n = len(response_times)
            median_response_time = response_times[n // 2] if n % 2 == 1 else (response_times[n // 2 - 1] + response_times[n // 2]) / 2
            p95_index = int(n * 0.95)
            p95_response_time = response_times[min(p95_index, n - 1)]
        
        if result:
            return {
                'avg_response_time': round(result.avg_response_time, 2) if result.avg_response_time else 0,
                'min_response_time': round(result.min_response_time, 2) if result.min_response_time else 0,
                'max_response_time': round(result.max_response_time, 2) if result.max_response_time else 0,
                'median_response_time': round(median_response_time, 2),
                'p95_response_time': round(p95_response_time, 2)
            }
        
        return {
            'avg_response_time': 0,
            'min_response_time': 0,
            'max_response_time': 0,
            'median_response_time': 0,
            'p95_response_time': 0
        }
    
    @staticmethod
    def get_system_overview(start_date=None, end_date=None):
        """Get overall system analytics overview"""
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()
        
        query = db.session.query(APIAnalytics).filter(
            APIAnalytics.timestamp >= start_date,
            APIAnalytics.timestamp <= end_date
        )
        
        total_requests = query.count()
        unique_endpoints = query.with_entities(distinct(APIAnalytics.endpoint)).count()
        unique_ips = query.filter(APIAnalytics.source_ip.isnot(None)).with_entities(distinct(APIAnalytics.source_ip)).count()
        
        # Error rate (4xx and 5xx)
        error_requests = query.filter(APIAnalytics.status_code >= 400).count()
        error_rate = (error_requests / total_requests * 100) if total_requests > 0 else 0
        
        # Get latest request
        latest_request = query.order_by(desc(APIAnalytics.timestamp)).first()
        
        # Handle dates properly - ensure they are datetime objects
        if isinstance(start_date, str):
            start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        if isinstance(end_date, str):
            end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        return {
            'total_requests': total_requests,
            'unique_endpoints': unique_endpoints,
            'unique_source_ips': unique_ips,
            'error_rate': round(error_rate, 2),
            'latest_request': latest_request.timestamp.isoformat() if latest_request and latest_request.timestamp else None,
            'date_range': {
                'start_date': start_date.isoformat() if hasattr(start_date, 'isoformat') else str(start_date),
                'end_date': end_date.isoformat() if hasattr(end_date, 'isoformat') else str(end_date)
            }
        }