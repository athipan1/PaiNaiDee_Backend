"""
Test docker-compose.yml configuration
"""
import yaml
import pytest
import os


def test_docker_compose_syntax():
    """Test that docker-compose.yml has valid YAML syntax"""
    compose_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'docker-compose.yml')
    
    with open(compose_file, 'r') as f:
        try:
            docker_compose = yaml.safe_load(f)
            assert docker_compose is not None
        except yaml.YAMLError as e:
            pytest.fail(f"docker-compose.yml has invalid YAML syntax: {e}")


def test_ai_assistant_service_exists():
    """Test that ai_assistant service is defined in docker-compose.yml"""
    compose_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'docker-compose.yml')
    
    with open(compose_file, 'r') as f:
        docker_compose = yaml.safe_load(f)
    
    assert 'services' in docker_compose
    assert 'ai_assistant' in docker_compose['services']


def test_ai_assistant_service_configuration():
    """Test that ai_assistant service has correct configuration"""
    compose_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'docker-compose.yml')
    
    with open(compose_file, 'r') as f:
        docker_compose = yaml.safe_load(f)
    
    ai_assistant = docker_compose['services']['ai_assistant']
    
    # Test build configuration
    assert 'build' in ai_assistant
    assert ai_assistant['build'] == 'https://github.com/athipan1/AI_Assistant_PaiNaiDee.git'
    
    # Test port configuration
    assert 'ports' in ai_assistant
    assert '8001:8001' in ai_assistant['ports']


def test_required_services_exist():
    """Test that all required services exist in docker-compose.yml"""
    compose_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'docker-compose.yml')
    
    with open(compose_file, 'r') as f:
        docker_compose = yaml.safe_load(f)
    
    required_services = ['backend', 'db', 'frontend', 'map3d', 'ai_assistant']
    
    for service in required_services:
        assert service in docker_compose['services'], f"Required service '{service}' not found"


def test_port_conflicts():
    """Test that services don't have conflicting port mappings"""
    compose_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'docker-compose.yml')
    
    with open(compose_file, 'r') as f:
        docker_compose = yaml.safe_load(f)
    
    used_ports = []
    
    for service_name, service_config in docker_compose['services'].items():
        if 'ports' in service_config:
            for port_mapping in service_config['ports']:
                if isinstance(port_mapping, str):
                    host_port = port_mapping.split(':')[0]
                    assert host_port not in used_ports, f"Port {host_port} is used by multiple services"
                    used_ports.append(host_port)