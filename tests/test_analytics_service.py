import pytest
from datetime import datetime, timedelta
from app.models import db
from app.models.api_analytics import APIAnalytics
from app.services.analytics_service import AnalyticsService


class TestAnalyticsService:
    """Test cases for the AnalyticsService"""
    
    def test_endpoint_summary_empty_data(self, app):
        """Test endpoint summary with no data"""
        with app.app_context():
            result = AnalyticsService.get_endpoint_summary()
            assert result == []
    
    def test_endpoint_summary_with_data(self, app):
        """Test endpoint summary with sample data"""
        with app.app_context():
            # Create sample analytics data
            analytics1 = APIAnalytics(
                endpoint='/api/attractions',
                method='GET',
                status_code=200,
                response_time=150.5,
                source_ip='192.168.1.1'
            )
            analytics2 = APIAnalytics(
                endpoint='/api/attractions',
                method='GET',
                status_code=200,
                response_time=200.0,
                source_ip='192.168.1.2'
            )
            analytics3 = APIAnalytics(
                endpoint='/api/reviews',
                method='POST',
                status_code=201,
                response_time=300.0,
                source_ip='192.168.1.1'
            )
            
            db.session.add_all([analytics1, analytics2, analytics3])
            db.session.commit()
            
            result = AnalyticsService.get_endpoint_summary()
            
            assert len(result) == 2
            
            # Check GET /api/attractions summary
            attractions_summary = next(r for r in result if r['endpoint'] == '/api/attractions')
            assert attractions_summary['method'] == 'GET'
            assert attractions_summary['request_count'] == 2
            assert attractions_summary['avg_response_time'] == 175.25  # (150.5 + 200.0) / 2
            assert attractions_summary['min_response_time'] == 150.5
            assert attractions_summary['max_response_time'] == 200.0
            
            # Check POST /api/reviews summary
            reviews_summary = next(r for r in result if r['endpoint'] == '/api/reviews')
            assert reviews_summary['method'] == 'POST'
            assert reviews_summary['request_count'] == 1
            assert reviews_summary['avg_response_time'] == 300.0
    
    def test_request_count_by_period_day(self, app):
        """Test request count grouped by day"""
        with app.app_context():
            now = datetime.utcnow()
            yesterday = now - timedelta(days=1)
            
            # Create analytics for today and yesterday
            analytics_today = APIAnalytics(
                endpoint='/api/attractions',
                method='GET',
                status_code=200,
                response_time=150.0,
                timestamp=now
            )
            analytics_yesterday = APIAnalytics(
                endpoint='/api/attractions',
                method='GET',
                status_code=200,
                response_time=150.0,
                timestamp=yesterday
            )
            
            db.session.add_all([analytics_today, analytics_yesterday])
            db.session.commit()
            
            start_date = yesterday - timedelta(hours=1)
            end_date = now + timedelta(hours=1)
            
            result = AnalyticsService.get_request_count_by_period(
                period='day',
                start_date=start_date,
                end_date=end_date
            )
            
            assert len(result) == 2
            assert all('period' in r and 'request_count' in r for r in result)
    
    def test_status_code_distribution(self, app):
        """Test status code distribution"""
        with app.app_context():
            # Create analytics with different status codes
            analytics_200 = APIAnalytics(
                endpoint='/api/attractions',
                method='GET',
                status_code=200,
                response_time=150.0
            )
            analytics_404 = APIAnalytics(
                endpoint='/api/nonexistent',
                method='GET',
                status_code=404,
                response_time=50.0
            )
            analytics_500 = APIAnalytics(
                endpoint='/api/error',
                method='GET',
                status_code=500,
                response_time=1000.0
            )
            
            db.session.add_all([analytics_200, analytics_404, analytics_500])
            db.session.commit()
            
            result = AnalyticsService.get_status_code_distribution()
            
            assert len(result) == 3
            
            status_codes = [r['status_code'] for r in result]
            assert 200 in status_codes
            assert 404 in status_codes
            assert 500 in status_codes
            
            # Check percentages sum to 100 (approximately)
            total_percentage = sum(r['percentage'] for r in result)
            assert abs(total_percentage - 100.0) < 0.1
    
    def test_top_source_ips(self, app):
        """Test top source IPs functionality"""
        with app.app_context():
            # Create analytics with different source IPs
            for i in range(5):
                analytics = APIAnalytics(
                    endpoint='/api/attractions',
                    method='GET',
                    status_code=200,
                    response_time=150.0,
                    source_ip='192.168.1.1'
                )
                db.session.add(analytics)
            
            for i in range(3):
                analytics = APIAnalytics(
                    endpoint='/api/attractions',
                    method='GET',
                    status_code=200,
                    response_time=150.0,
                    source_ip='192.168.1.2'
                )
                db.session.add(analytics)
            
            db.session.commit()
            
            result = AnalyticsService.get_top_source_ips(limit=5)
            
            assert len(result) == 2
            
            # Check that IPs are ordered by request count
            assert result[0]['source_ip'] == '192.168.1.1'
            assert result[0]['request_count'] == 5
            assert result[1]['source_ip'] == '192.168.1.2'
            assert result[1]['request_count'] == 3
    
    def test_response_time_analytics(self, app):
        """Test response time analytics"""
        with app.app_context():
            # Create analytics with different response times
            response_times = [100.0, 150.0, 200.0, 250.0, 300.0]
            
            for rt in response_times:
                analytics = APIAnalytics(
                    endpoint='/api/attractions',
                    method='GET',
                    status_code=200,
                    response_time=rt
                )
                db.session.add(analytics)
            
            db.session.commit()
            
            result = AnalyticsService.get_response_time_analytics()
            
            assert result['avg_response_time'] == 200.0  # (100+150+200+250+300)/5
            assert result['min_response_time'] == 100.0
            assert result['max_response_time'] == 300.0
            assert result['median_response_time'] == 200.0
    
    def test_system_overview(self, app):
        """Test system overview analytics"""
        with app.app_context():
            # Create sample analytics data
            analytics_data = [
                APIAnalytics(
                    endpoint='/api/attractions',
                    method='GET',
                    status_code=200,
                    response_time=150.0,
                    source_ip='192.168.1.1'
                ),
                APIAnalytics(
                    endpoint='/api/reviews',
                    method='POST',
                    status_code=404,
                    response_time=50.0,
                    source_ip='192.168.1.2'
                ),
                APIAnalytics(
                    endpoint='/api/attractions/:id',
                    method='GET',
                    status_code=500,
                    response_time=1000.0,
                    source_ip='192.168.1.1'
                )
            ]
            
            db.session.add_all(analytics_data)
            db.session.commit()
            
            result = AnalyticsService.get_system_overview()
            
            assert result['total_requests'] == 3
            assert result['unique_endpoints'] == 3  # /api/attractions, /api/reviews, and /api/attractions/:id
            assert result['unique_source_ips'] == 2
            assert result['error_rate'] == 66.67  # 2 errors out of 3 requests
            assert 'latest_request' in result
            assert 'date_range' in result