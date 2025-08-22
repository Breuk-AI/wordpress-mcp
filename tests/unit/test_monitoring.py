"""
Unit tests for monitoring.py - Pure functions only
Phase 3 of CI Enhancement
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import time
from datetime import datetime

# Import modules to test
from monitoring import MetricsCollector, HealthChecker, AlertManager


class TestMetricsCollector:
    """Test MetricsCollector pure functions"""
    
    def test_format_uptime_seconds_only(self):
        """Test formatting uptime with seconds only"""
        collector = MetricsCollector()
        
        assert collector._format_uptime(0) == "0s"
        assert collector._format_uptime(1) == "1s"
        assert collector._format_uptime(59) == "59s"
    
    def test_format_uptime_minutes(self):
        """Test formatting uptime with minutes"""
        collector = MetricsCollector()
        
        assert collector._format_uptime(60) == "1m 0s"
        assert collector._format_uptime(61) == "1m 1s"
        assert collector._format_uptime(119) == "1m 59s"
        assert collector._format_uptime(120) == "2m 0s"
    
    def test_format_uptime_hours(self):
        """Test formatting uptime with hours"""
        collector = MetricsCollector()
        
        assert collector._format_uptime(3600) == "1h 0m 0s"
        assert collector._format_uptime(3661) == "1h 1m 1s"
        assert collector._format_uptime(7200) == "2h 0m 0s"
        assert collector._format_uptime(3665) == "1h 1m 5s"
    
    def test_format_uptime_days(self):
        """Test formatting uptime with days"""
        collector = MetricsCollector()
        
        assert collector._format_uptime(86400) == "1d 0h 0m 0s"
        assert collector._format_uptime(86461) == "1d 0h 1m 1s"
        assert collector._format_uptime(90061) == "1d 1h 1m 1s"
        assert collector._format_uptime(172800) == "2d 0h 0m 0s"
    
    def test_format_uptime_complex(self):
        """Test formatting complex uptime values"""
        collector = MetricsCollector()
        
        # 2 days, 3 hours, 4 minutes, 5 seconds
        seconds = 2 * 86400 + 3 * 3600 + 4 * 60 + 5
        assert collector._format_uptime(seconds) == "2d 3h 4m 5s"
        
        # Large value
        assert collector._format_uptime(1000000) == "11d 13h 46m 40s"
    
    def test_format_uptime_edge_cases(self):
        """Test edge cases for uptime formatting"""
        collector = MetricsCollector()
        
        # Negative values (shouldn't happen but handle gracefully)
        assert collector._format_uptime(-1) == "0s"
        
        # Float values (round down)
        assert collector._format_uptime(60.7) == "1m 0s"
        assert collector._format_uptime(61.9) == "1m 1s"


class TestHealthChecker:
    """Test HealthChecker pure functions"""
    
    def test_is_healthy_all_true(self):
        """Test when all components are healthy"""
        checker = HealthChecker()
        checker.healthy = True
        checker.components = {
            'wordpress_connection': True,
            'rate_limiter': True,
            'session_manager': True,
            'auth_manager': True
        }
        
        assert checker.is_healthy() is True
    
    def test_is_healthy_main_false(self):
        """Test when main health is false"""
        checker = HealthChecker()
        checker.healthy = False
        checker.components = {
            'wordpress_connection': True,
            'rate_limiter': True,
            'session_manager': True,
            'auth_manager': True
        }
        
        assert checker.is_healthy() is False
    
    def test_is_healthy_component_false(self):
        """Test when a component is unhealthy"""
        checker = HealthChecker()
        checker.healthy = True
        checker.components = {
            'wordpress_connection': False,  # One component unhealthy
            'rate_limiter': True,
            'session_manager': True,
            'auth_manager': True
        }
        
        assert checker.is_healthy() is False
    
    def test_is_healthy_multiple_issues(self):
        """Test when multiple components are unhealthy"""
        checker = HealthChecker()
        checker.healthy = True
        checker.components = {
            'wordpress_connection': False,
            'rate_limiter': False,
            'session_manager': True,
            'auth_manager': False
        }
        
        assert checker.is_healthy() is False
    
    def test_is_healthy_empty_components(self):
        """Test with no components defined"""
        checker = HealthChecker()
        checker.healthy = True
        checker.components = {}
        
        assert checker.is_healthy() is True
    
    @patch('time.time')
    def test_get_uptime(self, mock_time):
        """Test uptime calculation"""
        mock_time.return_value = 1000.0
        
        checker = HealthChecker()
        checker.start_time = 900.0
        
        assert checker.get_uptime() == 100.0
    
    @patch('time.time')
    def test_get_uptime_zero(self, mock_time):
        """Test uptime when just started"""
        mock_time.return_value = 1000.0
        
        checker = HealthChecker()
        checker.start_time = 1000.0
        
        assert checker.get_uptime() == 0.0


class TestAlertManager:
    """Test AlertManager helper functions"""
    
    def test_create_alert_dict_structure(self):
        """Test that alert dictionary has correct structure"""
        # Note: _create_alert has side effects, but we can test 
        # the dictionary structure it creates
        manager = AlertManager()
        
        # Mock datetime to control timestamp
        with patch('monitoring.datetime') as mock_datetime:
            mock_datetime.now.return_value.isoformat.return_value = "2025-01-01T12:00:00"
            
            alert = manager._create_alert(
                alert_type="test_alert",
                severity="warning",
                message="Test message"
            )
            
            assert alert['type'] == "test_alert"
            assert alert['severity'] == "warning"
            assert alert['message'] == "Test message"
            assert alert['timestamp'] == "2025-01-01T12:00:00"
    
    def test_check_alerts_high_error_rate(self):
        """Test alert generation for high error rate"""
        manager = AlertManager(thresholds={'error_rate': 0.1})
        
        metrics = {
            'total_requests': 1000,
            'failed_requests': 200,  # 20% error rate
            'response_times': {},
            'rate_limited': 0
        }
        
        alerts = manager.check_alerts(metrics)
        
        assert len(alerts) > 0
        assert any(alert['type'] == 'high_error_rate' for alert in alerts)
    
    def test_check_alerts_no_issues(self):
        """Test no alerts when everything is fine"""
        manager = AlertManager(thresholds={
            'error_rate': 0.1,
            'response_time': 5.0,
            'rate_limit_hits': 100
        })
        
        metrics = {
            'total_requests': 1000,
            'failed_requests': 10,  # 1% error rate (below threshold)
            'response_times': {
                'tool1': {'avg': 1.0, 'min': 0.5, 'max': 2.0},
                'tool2': {'avg': 2.0, 'min': 1.0, 'max': 3.0}
            },
            'rate_limited': 10  # Below threshold
        }
        
        alerts = manager.check_alerts(metrics)
        
        assert len(alerts) == 0
    
    def test_check_alerts_slow_response(self):
        """Test alert for slow response times"""
        manager = AlertManager(thresholds={'response_time': 2.0})
        
        metrics = {
            'total_requests': 100,
            'failed_requests': 0,
            'response_times': {
                'slow_tool': {'avg': 5.5, 'min': 1.0, 'max': 10.0}  # Above threshold
            },
            'rate_limited': 0
        }
        
        alerts = manager.check_alerts(metrics)
        
        assert len(alerts) > 0
        assert any(alert['type'] == 'slow_response' for alert in alerts)


# Run tests with: pytest tests/unit/test_monitoring.py -v
