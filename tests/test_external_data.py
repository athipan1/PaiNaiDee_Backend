"""
Test cases for External Data Integration System

Tests the external data service, scheduler, and API routes.
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import json

from src.services.external_data_service import (
    ExternalDataService, AttractionData, UpdateResult
)
from src.services.data_update_scheduler import (
    DataUpdateScheduler, UpdateFrequency, UpdateStatus
)


class TestExternalDataService:
    """Test cases for ExternalDataService"""

    def setup_method(self):
        """Set up test fixtures"""
        self.service = ExternalDataService()

    def test_initialize_data_sources(self):
        """Test data sources initialization"""
        sources = self.service.data_sources
        
        assert 'google_places' in sources
        assert 'tat_api' in sources
        assert 'tripadvisor' in sources
        
        # Check default configurations
        assert sources['google_places'].enabled == False  # Requires API key
        assert sources['tat_api'].enabled == True
        assert sources['tripadvisor'].enabled == False  # Requires API key

    def test_configure_source(self):
        """Test configuring a data source"""
        self.service.configure_source(
            source_name='google_places',
            api_key='test-api-key',
            enabled=True,
            headers={'X-Custom': 'test'}
        )
        
        source = self.service.data_sources['google_places']
        assert source.api_key == 'test-api-key'
        assert source.enabled == True
        assert source.headers == {'X-Custom': 'test'}

    def test_get_source_status(self):
        """Test getting source status"""
        status = self.service.get_source_status()
        
        assert isinstance(status, dict)
        assert 'google_places' in status
        assert 'tat_api' in status
        assert 'tripadvisor' in status
        
        for source_name, source_status in status.items():
            assert 'enabled' in source_status
            assert 'configured' in source_status
            assert 'rate_limit' in source_status

    @patch('src.services.external_data_service.requests.get')
    def test_fetch_from_google_places_disabled(self, mock_get):
        """Test Google Places fetch when disabled"""
        results = self.service.fetch_from_google_places("temples")
        assert results == []
        mock_get.assert_not_called()

    def test_fetch_from_tat_api_mock_data(self):
        """Test TAT API fetch with mock data"""
        # Mock the _get_mock_tat_data method
        mock_data = [
            {
                'id': 1,
                'name': 'Test Temple',
                'description': 'A beautiful temple',
                'province': 'Bangkok',
                'district': 'Test District',
                'latitude': 13.7563,
                'longitude': 100.5018,
                'category': 'Temple',
                'main_image_url': 'http://example.com/image.jpg',
                'image_urls': [{'value': ['http://example.com/1.jpg']}]
            }
        ]
        
        with patch.object(self.service, '_get_mock_tat_data', return_value=mock_data):
            results = self.service.fetch_from_tat_api()
            
        assert len(results) == 1
        assert isinstance(results[0], AttractionData)
        assert results[0].name == 'Test Temple'
        assert results[0].province == 'Bangkok'

    def test_parse_tat_place(self):
        """Test parsing TAT place data"""
        place_data = {
            'id': 123,
            'name': 'Wat Phra Kaew',
            'description': 'Temple of the Emerald Buddha',
            'province': 'กรุงเทพมหานคร',
            'district': 'พระนคร',
            'address': 'Na Phra Lan Road',
            'latitude': 13.7515,
            'longitude': 100.4925,
            'category': 'วัด',
            'opening_hours': '08:30-15:30',
            'entrance_fee': '500 THB',
            'contact_phone': '02-623-5500',
            'website': 'http://www.watphrakaew.com',
            'main_image_url': 'http://example.com/main.jpg',
            'image_urls': [{'value': ['http://example.com/1.jpg', 'http://example.com/2.jpg']}]
        }
        
        result = self.service._parse_tat_place(place_data, 'tat_api')
        
        assert result is not None
        assert isinstance(result, AttractionData)
        assert result.external_id == 'tat_123'
        assert result.name == 'Wat Phra Kaew'
        assert result.province == 'กรุงเทพมหานคร'
        assert result.latitude == 13.7515
        assert result.longitude == 100.4925
        assert result.source == 'tat_api'
        assert len(result.image_urls) == 2

    def test_extract_province_from_address(self):
        """Test province extraction from address"""
        # Test Thai province name
        address1 = "123 ถนนสุขุมวิท กรุงเทพมหานคร 10110"
        province1 = self.service._extract_province_from_address(address1)
        assert province1 == 'กรุงเทพมหานคร'
        
        # Test English province name
        address2 = "123 Beach Road, Phuket, Thailand"
        province2 = self.service._extract_province_from_address(address2)
        assert province2 == 'ภูเก็ต'
        
        # Test no province found
        address3 = "Some random address"
        province3 = self.service._extract_province_from_address(address3)
        assert province3 == ""

    def test_categorize_place(self):
        """Test place categorization"""
        # Test with list of types
        types1 = ['tourist_attraction', 'temple', 'place_of_worship']
        category1 = self.service._categorize_place(types1)
        assert category1 == 'วัด'
        
        # Test with single type  
        category2 = self.service._categorize_place(['natural_feature'])
        assert category2 == 'ธรรมชาติ'
        
        # Test with unknown type
        category3 = self.service._categorize_place(['unknown_type'])
        assert category3 == 'สถานที่ท่องเที่ยว'

    def test_calculate_similarity(self):
        """Test string similarity calculation"""
        # Test exact match
        similarity1 = self.service._calculate_similarity("Temple", "Temple")
        assert similarity1 == 1.0
        
        # Test similar strings
        similarity2 = self.service._calculate_similarity("Wat Phra Kaew", "Wat Phrakaew")
        assert similarity2 > 0.8
        
        # Test different strings
        similarity3 = self.service._calculate_similarity("Temple", "Beach")
        assert similarity3 < 0.5

    def test_update_result_dataclass(self):
        """Test UpdateResult dataclass"""
        result = UpdateResult(
            success=True,
            total_processed=10,
            new_created=5,
            existing_updated=3,
            source='tat_api'
        )
        
        assert result.success == True
        assert result.total_processed == 10
        assert result.new_created == 5
        assert result.existing_updated == 3
        assert result.source == 'tat_api'
        assert isinstance(result.errors, list)
        assert isinstance(result.timestamp, datetime)


class TestDataUpdateScheduler:
    """Test cases for DataUpdateScheduler"""

    def setup_method(self):
        """Set up test fixtures"""
        self.external_service = MagicMock(spec=ExternalDataService)
        self.scheduler = DataUpdateScheduler(self.external_service)

    def test_add_scheduled_update(self):
        """Test adding a scheduled update"""
        schedule_id = self.scheduler.add_scheduled_update(
            source_name='tat_api',
            frequency=UpdateFrequency.DAILY,
            enabled=True,
            parameters={'province': 'Bangkok'}
        )
        
        assert schedule_id in self.scheduler.scheduled_updates
        
        schedule = self.scheduler.scheduled_updates[schedule_id]
        assert schedule.source_name == 'tat_api'
        assert schedule.frequency == UpdateFrequency.DAILY
        assert schedule.enabled == True
        assert schedule.parameters == {'province': 'Bangkok'}
        assert schedule.next_run is not None

    def test_update_scheduled_update(self):
        """Test updating a scheduled update"""
        # First add a schedule
        schedule_id = self.scheduler.add_scheduled_update(
            source_name='tat_api',
            frequency=UpdateFrequency.DAILY
        )
        
        # Update it
        success = self.scheduler.update_scheduled_update(
            schedule_id,
            enabled=False,
            frequency=UpdateFrequency.WEEKLY,
            parameters={'test': 'value'}
        )
        
        assert success == True
        
        schedule = self.scheduler.scheduled_updates[schedule_id]
        assert schedule.enabled == False
        assert schedule.frequency == UpdateFrequency.WEEKLY
        assert 'test' in schedule.parameters

    def test_remove_scheduled_update(self):
        """Test removing a scheduled update"""
        # Add a schedule
        schedule_id = self.scheduler.add_scheduled_update(
            source_name='tat_api',
            frequency=UpdateFrequency.DAILY
        )
        
        # Remove it
        success = self.scheduler.remove_scheduled_update(schedule_id)
        assert success == True
        assert schedule_id not in self.scheduler.scheduled_updates
        
        # Try to remove non-existent schedule
        success2 = self.scheduler.remove_scheduled_update('non-existent')
        assert success2 == False

    def test_trigger_manual_update(self):
        """Test triggering a manual update"""
        # Mock the external service
        mock_result = UpdateResult(success=True, source='tat_api')
        self.external_service.update_attractions_from_source.return_value = mock_result
        
        task_id = self.scheduler.trigger_manual_update(
            source_name='tat_api',
            parameters={'province': 'Bangkok'}
        )
        
        assert task_id in self.scheduler.update_tasks
        
        task = self.scheduler.update_tasks[task_id]
        assert task.source_name == 'tat_api'
        # Task may be completed immediately in tests since it runs synchronously
        assert task.status in [UpdateStatus.PENDING, UpdateStatus.COMPLETED]
        assert task.parameters == {'province': 'Bangkok'}

    def test_calculate_next_run(self):
        """Test calculating next run times"""
        base_time = datetime(2024, 1, 1, 12, 0, 0)
        
        # Test different frequencies
        next_hourly = self.scheduler._calculate_next_run(
            UpdateFrequency.HOURLY, base_time
        )
        assert next_hourly == base_time + timedelta(hours=1)
        
        next_daily = self.scheduler._calculate_next_run(
            UpdateFrequency.DAILY, base_time
        )
        assert next_daily == base_time + timedelta(days=1)
        
        next_weekly = self.scheduler._calculate_next_run(
            UpdateFrequency.WEEKLY, base_time
        )
        assert next_weekly == base_time + timedelta(weeks=1)
        
        next_monthly = self.scheduler._calculate_next_run(
            UpdateFrequency.MONTHLY, base_time
        )
        assert next_monthly == base_time + timedelta(days=30)
        
        # Manual updates don't have next run
        next_manual = self.scheduler._calculate_next_run(UpdateFrequency.MANUAL)
        assert next_manual is None

    def test_get_scheduled_updates(self):
        """Test getting all scheduled updates"""
        # Add some schedules
        self.scheduler.add_scheduled_update('tat_api', UpdateFrequency.DAILY)
        self.scheduler.add_scheduled_update('google_places', UpdateFrequency.WEEKLY)
        
        schedules = self.scheduler.get_scheduled_updates()
        
        assert len(schedules) == 2
        assert all(isinstance(schedule, dict) for schedule in schedules)

    def test_get_update_tasks(self):
        """Test getting update tasks"""
        # Add some tasks
        task_id1 = self.scheduler.trigger_manual_update('tat_api')
        task_id2 = self.scheduler.trigger_manual_update('google_places')
        
        # Mark one as completed
        self.scheduler.update_tasks[task_id1].status = UpdateStatus.COMPLETED
        
        # Get all tasks
        all_tasks = self.scheduler.get_update_tasks()
        assert len(all_tasks) >= 2
        
        # Get filtered tasks
        completed_tasks = self.scheduler.get_update_tasks(
            status_filter=UpdateStatus.COMPLETED
        )
        assert len(completed_tasks) >= 1

    def test_get_scheduler_status(self):
        """Test getting scheduler status"""
        # Add some schedules and tasks
        self.scheduler.add_scheduled_update('tat_api', UpdateFrequency.DAILY)
        self.scheduler.add_scheduled_update('google_places', UpdateFrequency.WEEKLY, enabled=False)
        self.scheduler.trigger_manual_update('tat_api')
        
        status = self.scheduler.get_scheduler_status()
        
        assert 'is_running' in status
        assert 'active_schedules' in status
        assert 'total_schedules' in status
        assert 'running_tasks' in status
        assert 'pending_tasks' in status
        assert 'max_concurrent_tasks' in status
        
        assert status['active_schedules'] == 1  # Only enabled schedules
        assert status['total_schedules'] == 2


class TestExternalDataRoutes:
    """Test cases for External Data API routes"""

    @pytest.fixture
    def authenticated_headers(self, app, test_user):
        """Get authentication headers for requests"""
        from flask_jwt_extended import create_access_token
        
        with app.app_context():
            token = create_access_token(identity=test_user.id)
        
        return {'Authorization': f'Bearer {token}'}

    def test_get_data_sources(self, client, authenticated_headers):
        """Test getting data sources"""
        response = client.get('/api/external-data/sources', headers=authenticated_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == True
        assert 'sources' in data
        assert 'google_places' in data['sources']
        assert 'tat_api' in data['sources']

    def test_configure_data_source(self, client, authenticated_headers):
        """Test configuring a data source"""
        config_data = {
            'api_key': 'test-api-key',
            'enabled': True,
            'headers': {'X-Custom': 'test'}
        }
        
        response = client.post(
            '/api/external-data/sources/google_places/configure',
            json=config_data,
            headers=authenticated_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == True

    def test_trigger_manual_update(self, client, authenticated_headers):
        """Test triggering a manual update"""
        update_data = {
            'source_name': 'tat_api',
            'parameters': {'province': 'Bangkok'}
        }
        
        response = client.post(
            '/api/external-data/update/manual',
            json=update_data,
            headers=authenticated_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == True
        assert 'task_id' in data

    def test_trigger_manual_update_missing_source(self, client, authenticated_headers):
        """Test triggering update without source name"""
        response = client.post(
            '/api/external-data/update/manual',
            json={},
            headers=authenticated_headers
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] == False
        assert 'source_name is required' in data['error']

    def test_trigger_update_all_sources(self, client, authenticated_headers):
        """Test triggering updates for all sources"""
        response = client.post(
            '/api/external-data/update/all',
            json={'parameters': {'test': 'value'}},
            headers=authenticated_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == True
        assert 'task_ids' in data

    def test_create_scheduled_update(self, client, authenticated_headers):
        """Test creating a scheduled update"""
        schedule_data = {
            'source_name': 'tat_api',
            'frequency': 'daily',
            'enabled': True,
            'parameters': {'province': 'Bangkok'}
        }
        
        response = client.post(
            '/api/external-data/schedules',
            json=schedule_data,
            headers=authenticated_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == True
        assert 'schedule_id' in data

    def test_create_scheduled_update_invalid_frequency(self, client, authenticated_headers):
        """Test creating scheduled update with invalid frequency"""
        schedule_data = {
            'source_name': 'tat_api',
            'frequency': 'invalid',
            'enabled': True
        }
        
        response = client.post(
            '/api/external-data/schedules',
            json=schedule_data,
            headers=authenticated_headers
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] == False
        assert 'Invalid frequency' in data['error']

    def test_get_scheduled_updates(self, client, authenticated_headers):
        """Test getting scheduled updates"""
        response = client.get('/api/external-data/schedules', headers=authenticated_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == True
        assert 'schedules' in data

    def test_get_update_tasks(self, client, authenticated_headers):
        """Test getting update tasks"""
        response = client.get('/api/external-data/tasks', headers=authenticated_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == True
        assert 'tasks' in data

    def test_get_update_tasks_with_filters(self, client, authenticated_headers):
        """Test getting update tasks with filters"""
        response = client.get(
            '/api/external-data/tasks?limit=10&status=completed',
            headers=authenticated_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == True

    def test_get_scheduler_status(self, client, authenticated_headers):
        """Test getting scheduler status"""
        response = client.get(
            '/api/external-data/scheduler/status',
            headers=authenticated_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == True
        assert 'scheduler' in data

    def test_check_province_coverage(self, client, authenticated_headers):
        """Test checking province coverage"""
        response = client.get(
            '/api/external-data/coverage/provinces',
            headers=authenticated_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == True
        assert 'coverage' in data
        assert 'total_provinces' in data['coverage']
        assert 'covered_provinces' in data['coverage']
        assert 'coverage_percentage' in data['coverage']
        assert 'provinces' in data['coverage']

    def test_get_external_data_stats(self, client, authenticated_headers):
        """Test getting external data statistics"""
        response = client.get('/api/external-data/stats', headers=authenticated_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == True
        assert 'stats' in data
        assert 'scheduler_status' in data

    def test_unauthorized_access(self, client):
        """Test unauthorized access to external data endpoints"""
        response = client.get('/api/external-data/sources')
        assert response.status_code == 401

    def test_get_update_history(self, client, authenticated_headers):
        """Test getting update history"""
        response = client.get('/api/external-data/history', headers=authenticated_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == True
        assert 'history' in data