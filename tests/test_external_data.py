import pytest
import json
from src.app import create_app
from src.models import db
from src.models.external_data import DataSource, ManualUpdate, ScheduledUpdate


@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def sample_data_sources():
    """Create sample data sources for testing"""
    sources = [
        DataSource(name="API Source 1", type="api", endpoint_url="https://api.example.com/data", is_active=True),
        DataSource(name="Database Source", type="database", is_active=True),
        DataSource(name="File Source", type="file", is_active=False),
        DataSource(name="API Source 2", type="api", endpoint_url="https://api2.example.com/data", is_active=True)
    ]
    
    for source in sources:
        db.session.add(source)
    db.session.commit()
    
    return sources


class TestExternalData:
    
    def test_get_data_sources(self, client, sample_data_sources):
        """Test getting all data sources - should return 4 sources"""
        response = client.get('/api/external-data/sources')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['data']) == 4
        assert data['message'] == "Data sources retrieved successfully"
    
    def test_get_data_sources_empty(self, client):
        """Test getting data sources when none exist"""
        response = client.get('/api/external-data/sources')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['data']) == 0
    
    def test_configure_data_source_create_new(self, client):
        """Test creating a new data source"""
        payload = {
            "name": "New API Source",
            "type": "api",
            "endpoint_url": "https://newapi.example.com/data",
            "configuration": {"timeout": 30, "retries": 3},
            "is_active": True
        }
        
        response = client.post('/api/external-data/configure', 
                             data=json.dumps(payload),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['data']['name'] == "New API Source"
        assert data['data']['type'] == "api"
        assert data['message'] == "Data source configured successfully"
    
    def test_configure_data_source_missing_required_fields(self, client):
        """Test configuring data source with missing required fields"""
        payload = {
            "type": "api"  # Missing 'name'
        }
        
        response = client.post('/api/external-data/configure',
                             data=json.dumps(payload),
                             content_type='application/json')
        
        assert response.status_code == 422
        data = json.loads(response.data)
        assert "Missing required fields" in data['message']
    
    def test_configure_data_source_invalid_type(self, client):
        """Test configuring data source with invalid type"""
        payload = {
            "name": "Invalid Source",
            "type": "invalid_type"
        }
        
        response = client.post('/api/external-data/configure',
                             data=json.dumps(payload),
                             content_type='application/json')
        
        assert response.status_code == 422
        data = json.loads(response.data)
        assert "Invalid type" in data['message']
    
    def test_configure_data_source_duplicate_name(self, client, sample_data_sources):
        """Test configuring data source with duplicate name"""
        payload = {
            "name": "API Source 1",  # This name already exists
            "type": "api"
        }
        
        response = client.post('/api/external-data/configure',
                             data=json.dumps(payload),
                             content_type='application/json')
        
        assert response.status_code == 422
        data = json.loads(response.data)
        assert "Data source with this name already exists" in data['message']
    
    def test_trigger_manual_update(self, client, sample_data_sources):
        """Test triggering manual update for a data source"""
        source = sample_data_sources[0]  # Use first active source
        
        payload = {
            "data_source_id": source.id,
            "triggered_by": "test_user",
            "expected_records": 100
        }
        
        response = client.post('/api/external-data/trigger-update',
                             data=json.dumps(payload),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['data']['data_source_id'] == source.id
        assert data['data']['status'] == 'completed'
        assert data['data']['records_processed'] == 100
        assert data['message'] == "Manual update triggered successfully"
    
    def test_trigger_manual_update_missing_data_source_id(self, client):
        """Test triggering manual update without data_source_id"""
        payload = {
            "triggered_by": "test_user"
        }
        
        response = client.post('/api/external-data/trigger-update',
                             data=json.dumps(payload),
                             content_type='application/json')
        
        assert response.status_code == 422
        data = json.loads(response.data)
        assert "data_source_id is required" in data['message']
    
    def test_trigger_manual_update_invalid_data_source(self, client):
        """Test triggering manual update with invalid data source ID"""
        payload = {
            "data_source_id": 999,  # Non-existent ID
            "triggered_by": "test_user"
        }
        
        response = client.post('/api/external-data/trigger-update',
                             data=json.dumps(payload),
                             content_type='application/json')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert "Data source not found" in data['message']
    
    def test_trigger_manual_update_inactive_source(self, client, sample_data_sources):
        """Test triggering manual update for inactive data source"""
        inactive_source = sample_data_sources[2]  # File Source is inactive
        
        payload = {
            "data_source_id": inactive_source.id,
            "triggered_by": "test_user"
        }
        
        response = client.post('/api/external-data/trigger-update',
                             data=json.dumps(payload),
                             content_type='application/json')
        
        assert response.status_code == 422
        data = json.loads(response.data)
        assert "Cannot trigger update for inactive data source" in data['message']
    
    def test_create_scheduled_update(self, client, sample_data_sources):
        """Test creating a scheduled update"""
        source = sample_data_sources[0]
        
        payload = {
            "data_source_id": source.id,
            "frequency": "daily",
            "is_active": True
        }
        
        response = client.post('/api/external-data/scheduled-update',
                             data=json.dumps(payload),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['data']['data_source_id'] == source.id
        assert data['data']['frequency'] == "daily"
        assert data['data']['is_active'] is True
        assert data['message'] == "Scheduled update created successfully"
    
    def test_create_scheduled_update_invalid_frequency(self, client, sample_data_sources):
        """Test creating scheduled update with invalid frequency"""
        source = sample_data_sources[0]
        
        payload = {
            "data_source_id": source.id,
            "frequency": "invalid_frequency"
        }
        
        response = client.post('/api/external-data/scheduled-update',
                             data=json.dumps(payload),
                             content_type='application/json')
        
        assert response.status_code == 422
        data = json.loads(response.data)
        assert "Invalid frequency" in data['message']
    
    def test_create_scheduled_update_missing_fields(self, client):
        """Test creating scheduled update with missing required fields"""
        payload = {
            "frequency": "daily"  # Missing data_source_id
        }
        
        response = client.post('/api/external-data/scheduled-update',
                             data=json.dumps(payload),
                             content_type='application/json')
        
        assert response.status_code == 422
        data = json.loads(response.data)
        assert "Missing required fields" in data['message']
    
    def test_create_scheduled_update_invalid_data_source(self, client):
        """Test creating scheduled update with invalid data source ID"""
        payload = {
            "data_source_id": 999,  # Non-existent ID
            "frequency": "daily"
        }
        
        response = client.post('/api/external-data/scheduled-update',
                             data=json.dumps(payload),
                             content_type='application/json')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert "Data source not found" in data['message']
    
    def test_create_scheduled_update_duplicate(self, client, sample_data_sources):
        """Test creating duplicate scheduled update for same data source"""
        source = sample_data_sources[0]
        
        # Create first scheduled update
        scheduled_update = ScheduledUpdate(
            data_source_id=source.id,
            frequency="daily",
            is_active=True
        )
        db.session.add(scheduled_update)
        db.session.commit()
        
        # Try to create another one for the same source
        payload = {
            "data_source_id": source.id,
            "frequency": "weekly"
        }
        
        response = client.post('/api/external-data/scheduled-update',
                             data=json.dumps(payload),
                             content_type='application/json')
        
        assert response.status_code == 422
        data = json.loads(response.data)
        assert "Active scheduled update already exists" in data['message']