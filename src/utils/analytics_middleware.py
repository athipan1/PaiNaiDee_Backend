import time
import sys
from flask import request, g
from flask_jwt_extended import get_current_user
from src.models import db
from src.models.api_analytics import APIAnalytics


class APIAnalyticsMiddleware:
    """Middleware to automatically track API request analytics"""
    
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize the middleware with Flask app"""
        app.before_request(self.before_request)
        app.after_request(self.after_request)
    
    def before_request(self):
        """Record request start time and metadata"""
        g.start_time = time.time()
        g.request_size = request.content_length or 0
    
    def after_request(self, response):
        """Record analytics data after request processing"""
        try:
            # Skip static files and non-API routes
            if (request.endpoint and 
                (request.endpoint.startswith('static') or 
                 not request.path.startswith('/api'))):
                return response
            
            # Calculate response time in milliseconds
            response_time = (time.time() - g.get('start_time', time.time())) * 1000
            
            # Get current user if authenticated
            user_id = None
            try:
                current_user = get_current_user()
                if current_user:
                    user_id = current_user.id
            except:
                pass  # No authenticated user
            
            # Get response size
            response_size = 0
            if hasattr(response, 'content_length') and response.content_length:
                response_size = response.content_length
            elif hasattr(response, 'data'):
                response_size = len(response.data)
            
            # Clean endpoint path for analytics (remove IDs and query params)
            endpoint_path = self._normalize_endpoint(request.path)
            
            # Create analytics record
            analytics = APIAnalytics(
                endpoint=endpoint_path,
                method=request.method,
                status_code=response.status_code,
                response_time=response_time,
                source_ip=self._get_client_ip(),
                user_agent=request.headers.get('User-Agent', ''),
                request_size=g.get('request_size', 0),
                response_size=response_size,
                user_id=user_id
            )
            
            db.session.add(analytics)
            db.session.commit()
            
        except Exception as e:
            # Log error but don't break the response
            print(f"Analytics middleware error: {e}", file=sys.stderr)
            try:
                db.session.rollback()
            except:
                pass
        
        return response
    
    def _get_client_ip(self):
        """Get the real client IP address"""
        if request.headers.get('X-Forwarded-For'):
            return request.headers.get('X-Forwarded-For').split(',')[0].strip()
        elif request.headers.get('X-Real-IP'):
            return request.headers.get('X-Real-IP')
        else:
            return request.remote_addr
    
    def _normalize_endpoint(self, path):
        """Normalize endpoint path for analytics grouping"""
        # Remove query parameters
        if '?' in path:
            path = path.split('?')[0]
        
        # Replace common ID patterns with placeholders
        import re
        
        # Replace numeric IDs
        path = re.sub(r'/\d+(?=/|$)', '/:id', path)
        
        # Replace UUID patterns
        path = re.sub(r'/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}(?=/|$)', '/:uuid', path)
        
        # Replace other common patterns
        path = re.sub(r'/[0-9a-zA-Z_-]{10,}(?=/|$)', '/:param', path)
        
        return path