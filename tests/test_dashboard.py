import pytest
import json
from datetime import datetime, timedelta
from src.models import db
from src.models.api_analytics import APIAnalytics


class TestDashboardRoutes:
    """Test cases for dashboard API routes"""
    
    def test_dashboard_overview_unauthorized(self, client):
        """Test dashboard overview without authentication"""
        response = client.get("/api/dashboard/overview")
        assert response.status_code == 401
    
    def test_dashboard_overview_authorized(self, client, auth_headers):
        """Test dashboard overview with authentication"""
        response = client.get("/api/dashboard/overview", headers=auth_headers)
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'data' in data
        assert 'total_requests' in data['data']
        assert 'unique_endpoints' in data['data']
        assert 'unique_source_ips' in data['data']
        assert 'error_rate' in data['data']
    
    def test_dashboard_endpoints_summary(self, client, auth_headers, app):
        """Test endpoints summary endpoint"""
        with app.app_context():
            # Create sample analytics data
            analytics = APIAnalytics(
                endpoint='/api/attractions',
                method='GET',
                status_code=200,
                response_time=150.0,
                source_ip='192.168.1.1'
            )
            db.session.add(analytics)
            db.session.commit()
            
            response = client.get("/api/dashboard/endpoints", headers=auth_headers)
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert data['success'] is True
            assert isinstance(data['data'], list)
            
            if data['data']:  # If there's data
                endpoint_data = data['data'][0]
                assert 'endpoint' in endpoint_data
                assert 'method' in endpoint_data
                assert 'request_count' in endpoint_data
                assert 'avg_response_time' in endpoint_data
    
    def test_dashboard_requests_by_period(self, client, auth_headers):
        """Test requests by period endpoint"""
        response = client.get("/api/dashboard/requests-by-period?period=day", headers=auth_headers)
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert isinstance(data['data'], list)
    
    def test_dashboard_requests_by_period_invalid_period(self, client, auth_headers):
        """Test requests by period with invalid period parameter"""
        response = client.get("/api/dashboard/requests-by-period?period=invalid", headers=auth_headers)
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'Invalid query parameters' in data['message']
    
    def test_dashboard_status_codes(self, client, auth_headers, app):
        """Test status code distribution endpoint"""
        with app.app_context():
            # Create analytics with different status codes
            analytics_data = [
                APIAnalytics(
                    endpoint='/api/attractions',
                    method='GET',
                    status_code=200,
                    response_time=150.0
                ),
                APIAnalytics(
                    endpoint='/api/nonexistent',
                    method='GET',
                    status_code=404,
                    response_time=50.0
                )
            ]
            db.session.add_all(analytics_data)
            db.session.commit()
            
            response = client.get("/api/dashboard/status-codes", headers=auth_headers)
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert data['success'] is True
            assert isinstance(data['data'], list)
            
            if data['data']:  # If there's data
                status_data = data['data'][0]
                assert 'status_code' in status_data
                assert 'count' in status_data
                assert 'percentage' in status_data
    
    def test_dashboard_source_ips(self, client, auth_headers, app):
        """Test top source IPs endpoint"""
        with app.app_context():
            # Create analytics with source IPs
            analytics = APIAnalytics(
                endpoint='/api/attractions',
                method='GET',
                status_code=200,
                response_time=150.0,
                source_ip='192.168.1.1'
            )
            db.session.add(analytics)
            db.session.commit()
            
            response = client.get("/api/dashboard/source-ips?limit=5", headers=auth_headers)
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert data['success'] is True
            assert isinstance(data['data'], list)
            
            if data['data']:  # If there's data
                ip_data = data['data'][0]
                assert 'source_ip' in ip_data
                assert 'request_count' in ip_data
    
    def test_dashboard_response_times(self, client, auth_headers, app):
        """Test response time analytics endpoint"""
        with app.app_context():
            # Create analytics with response times
            analytics = APIAnalytics(
                endpoint='/api/attractions',
                method='GET',
                status_code=200,
                response_time=150.0
            )
            db.session.add(analytics)
            db.session.commit()
            
            response = client.get("/api/dashboard/response-times", headers=auth_headers)
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert data['success'] is True
            assert 'data' in data
            
            response_time_data = data['data']
            assert 'avg_response_time' in response_time_data
            assert 'min_response_time' in response_time_data
            assert 'max_response_time' in response_time_data
            assert 'median_response_time' in response_time_data
            assert 'p95_response_time' in response_time_data
    
    def test_dashboard_with_date_filters(self, client, auth_headers):
        """Test dashboard endpoints with date range filters"""
        start_date = (datetime.utcnow() - timedelta(days=7)).isoformat()
        end_date = datetime.utcnow().isoformat()
        
        response = client.get(
            f"/api/dashboard/overview?start_date={start_date}&end_date={end_date}",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'data' in data
    
    def test_dashboard_invalid_date_format(self, client, auth_headers):
        """Test dashboard with invalid date format"""
        response = client.get(
            "/api/dashboard/overview?start_date=invalid-date",
            headers=auth_headers
        )
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'Invalid query parameters' in data['message']