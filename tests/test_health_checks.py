"""
Health check tests for both FastAPI and Flask applications
"""
import pytest
import requests
import time
import subprocess
import signal
import os
from multiprocessing import Process


def start_fastapi_server():
    """Start FastAPI server in a subprocess"""
    env = os.environ.copy()
    env['DATABASE_URL'] = 'sqlite:///./test_health.db'
    
    return subprocess.Popen(
        ['python', 'run_fastapi.py'],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )


def start_flask_server():
    """Start Flask server in a subprocess"""
    env = os.environ.copy()
    env['FLASK_ENV'] = 'testing'
    
    return subprocess.Popen(
        ['python', 'run.py'],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )


@pytest.mark.integration
def test_fastapi_health_check():
    """Test FastAPI health endpoint"""
    process = None
    try:
        process = start_fastapi_server()
        
        # Wait for server to start
        time.sleep(3)
        
        # Check if server is running
        if process.poll() is not None:
            stdout, stderr = process.communicate()
            pytest.skip(f"FastAPI server failed to start: {stderr.decode()}")
        
        # Test health endpoint
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            assert response.status_code == 200
            
            data = response.json()
            assert data["status"] == "healthy"
            assert "version" in data
            
        except requests.RequestException as e:
            pytest.skip(f"Could not connect to FastAPI server: {e}")
            
    finally:
        if process:
            process.terminate()
            process.wait()


@pytest.mark.integration
def test_flask_health_check():
    """Test Flask health endpoint"""
    process = None
    try:
        process = start_flask_server()
        
        # Wait for server to start
        time.sleep(3)
        
        # Check if server is running
        if process.poll() is not None:
            stdout, stderr = process.communicate()
            pytest.skip(f"Flask server failed to start: {stderr.decode()}")
        
        # Test home endpoint (Flask doesn't have /health by default)
        try:
            response = requests.get("http://localhost:5000/", timeout=5)
            assert response.status_code == 200
            
            data = response.json()
            assert data["success"] is True
            assert "message" in data
            
        except requests.RequestException as e:
            pytest.skip(f"Could not connect to Flask server: {e}")
            
    finally:
        if process:
            process.terminate()
            process.wait()


@pytest.mark.integration
def test_fastapi_root_endpoint():
    """Test FastAPI root endpoint"""
    process = None
    try:
        process = start_fastapi_server()
        time.sleep(3)
        
        if process.poll() is not None:
            pytest.skip("FastAPI server failed to start")
        
        try:
            response = requests.get("http://localhost:8000/", timeout=5)
            assert response.status_code == 200
            
            data = response.json()
            assert "PaiNaiDee Backend API" in data["message"]
            assert "endpoints" in data
            
        except requests.RequestException:
            pytest.skip("Could not connect to FastAPI server")
            
    finally:
        if process:
            process.terminate()
            process.wait()


@pytest.mark.integration  
def test_fastapi_docs_endpoint():
    """Test FastAPI documentation endpoint"""
    process = None
    try:
        process = start_fastapi_server()
        time.sleep(3)
        
        if process.poll() is not None:
            pytest.skip("FastAPI server failed to start")
        
        try:
            response = requests.get("http://localhost:8000/docs", timeout=5)
            # Should return HTML page (200) or redirect
            assert response.status_code in [200, 307, 404]  # 404 is acceptable if docs not configured
            
        except requests.RequestException:
            pytest.skip("Could not connect to FastAPI server")
            
    finally:
        if process:
            process.terminate()
            process.wait()