#!/usr/bin/env python3
"""
Dashboard API Example - Demonstrates how to use the dashboard endpoints

This script shows how to:
1. Authenticate with the API
2. Fetch dashboard data
3. Display the results in a readable format

Usage:
    python dashboard_example.py

Requirements:
    - A running PaiNaiDee Backend server
    - Valid user credentials
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Optional

class DashboardClient:
    """Client for interacting with the dashboard API"""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.token = None
    
    def login(self, username: str, password: str) -> bool:
        """Authenticate and get JWT token"""
        try:
            response = requests.post(f"{self.base_url}/api/auth/login", json={
                "username": username,
                "password": password
            })
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get('data', {}).get('access_token')
                return True
            else:
                print(f"Login failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"Login error: {e}")
            return False
    
    def _get_headers(self) -> dict:
        """Get headers with authentication"""
        if not self.token:
            raise Exception("Not authenticated. Call login() first.")
        
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    def get_overview(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> dict:
        """Get system overview"""
        params = {}
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
        
        response = requests.get(
            f"{self.base_url}/api/dashboard/overview",
            headers=self._get_headers(),
            params=params
        )
        return response.json()
    
    def get_endpoints(self) -> dict:
        """Get endpoints summary"""
        response = requests.get(
            f"{self.base_url}/api/dashboard/endpoints",
            headers=self._get_headers()
        )
        return response.json()
    
    def get_requests_by_period(self, period: str = "day") -> dict:
        """Get request count by period"""
        response = requests.get(
            f"{self.base_url}/api/dashboard/requests-by-period",
            headers=self._get_headers(),
            params={"period": period}
        )
        return response.json()
    
    def get_status_codes(self) -> dict:
        """Get status code distribution"""
        response = requests.get(
            f"{self.base_url}/api/dashboard/status-codes",
            headers=self._get_headers()
        )
        return response.json()
    
    def get_source_ips(self, limit: int = 10) -> dict:
        """Get top source IPs"""
        response = requests.get(
            f"{self.base_url}/api/dashboard/source-ips",
            headers=self._get_headers(),
            params={"limit": limit}
        )
        return response.json()
    
    def get_response_times(self) -> dict:
        """Get response time analytics"""
        response = requests.get(
            f"{self.base_url}/api/dashboard/response-times",
            headers=self._get_headers()
        )
        return response.json()

def print_section(title: str):
    """Print a section header"""
    print(f"\n{'='*60}")
    print(f"📊 {title}")
    print('='*60)

def format_datetime(dt_str: str) -> str:
    """Format datetime string for display"""
    if not dt_str:
        return "N/A"
    try:
        dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return dt_str

def main():
    """Main demonstration function"""
    print("🚀 PaiNaiDee Backend Dashboard API Example")
    print("=" * 60)
    
    # Initialize client
    client = DashboardClient()
    
    # Get credentials
    username = input("Enter username: ").strip()
    password = input("Enter password: ").strip()
    
    # Login
    print("\n🔐 Authenticating...")
    if not client.login(username, password):
        print("❌ Authentication failed!")
        return
    
    print("✅ Authentication successful!")
    
    try:
        # 1. System Overview
        print_section("System Overview")
        overview = client.get_overview()
        if overview['success']:
            data = overview['data']
            print(f"📈 Total Requests: {data['total_requests']:,}")
            print(f"🎯 Unique Endpoints: {data['unique_endpoints']}")
            print(f"🌐 Unique Source IPs: {data['unique_source_ips']}")
            print(f"⚠️ Error Rate: {data['error_rate']:.2f}%")
            print(f"🕒 Latest Request: {format_datetime(data.get('latest_request'))}")
        else:
            print(f"❌ Error: {overview['message']}")
        
        # 2. Top Endpoints
        print_section("Top Endpoints")
        endpoints = client.get_endpoints()
        if endpoints['success']:
            for i, endpoint in enumerate(endpoints['data'][:5], 1):
                print(f"{i:2d}. {endpoint['method']:6s} {endpoint['endpoint']:30s}")
                print(f"    📊 {endpoint['request_count']:4d} requests | "
                      f"⏱️ {endpoint['avg_response_time']:6.1f}ms avg | "
                      f"🕒 {format_datetime(endpoint.get('last_request'))}")
        else:
            print(f"❌ Error: {endpoints['message']}")
        
        # 3. Status Code Distribution
        print_section("Status Code Distribution")
        status_codes = client.get_status_codes()
        if status_codes['success']:
            for status in status_codes['data']:
                status_icon = "✅" if status['status_code'] < 400 else "⚠️" if status['status_code'] < 500 else "❌"
                print(f"{status_icon} HTTP {status['status_code']}: "
                      f"{status['count']:4d} requests ({status['percentage']:5.1f}%)")
        else:
            print(f"❌ Error: {status_codes['message']}")
        
        # 4. Response Time Analytics
        print_section("Response Time Analytics")
        response_times = client.get_response_times()
        if response_times['success']:
            data = response_times['data']
            print(f"⚡ Average: {data['avg_response_time']:8.2f}ms")
            print(f"🚀 Minimum: {data['min_response_time']:8.2f}ms")
            print(f"🐌 Maximum: {data['max_response_time']:8.2f}ms")
            print(f"📊 Median:  {data['median_response_time']:8.2f}ms")
            print(f"📈 95th %:  {data['p95_response_time']:8.2f}ms")
        else:
            print(f"❌ Error: {response_times['message']}")
        
        # 5. Top Source IPs
        print_section("Top Source IPs")
        source_ips = client.get_source_ips(limit=5)
        if source_ips['success']:
            for i, ip_data in enumerate(source_ips['data'], 1):
                print(f"{i:2d}. {ip_data['source_ip']:15s} | "
                      f"{ip_data['request_count']:4d} requests | "
                      f"🕒 {format_datetime(ip_data.get('last_request'))}")
        else:
            print(f"❌ Error: {source_ips['message']}")
        
        # 6. Request Trends (Last 7 days)
        print_section("Daily Request Trends")
        requests_by_day = client.get_requests_by_period(period="day")
        if requests_by_day['success']:
            for day_data in requests_by_day['data'][-7:]:  # Last 7 days
                print(f"📅 {day_data['period']}: {day_data['request_count']:4d} requests")
        else:
            print(f"❌ Error: {requests_by_day['message']}")
        
        print_section("Dashboard Example Complete!")
        print("🎉 All dashboard endpoints working correctly!")
        print("\nFor more detailed API documentation, see DASHBOARD_README.md")
        
    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()