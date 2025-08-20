"""
Monitoring and Health Check Module for WordPress MCP
Production-ready monitoring with metrics collection
"""

import time
import json
from typing import Dict, Any, Optional
from collections import defaultdict, deque
from datetime import datetime, timedelta
import asyncio
import logging

logger = logging.getLogger(__name__)

class MetricsCollector:
    """Collects and aggregates metrics for monitoring"""
    
    def __init__(self, window_size: int = 3600):
        """
        Initialize metrics collector
        
        Args:
            window_size: Time window in seconds for metrics (default 1 hour)
        """
        self.window_size = window_size
        self.start_time = time.time()
        
        # Counters
        self.counters = defaultdict(int)
        
        # Time series data (using deque for efficient windowing)
        self.request_times = defaultdict(lambda: deque(maxlen=1000))
        self.response_times = defaultdict(list)
        
        # Error tracking
        self.errors = defaultdict(int)
        self.last_errors = deque(maxlen=100)
        
        # Request tracking
        self.requests_per_minute = deque(maxlen=60)
        self._last_minute = int(time.time() / 60)
        self._current_minute_requests = 0
    
    def increment(self, metric: str, value: int = 1) -> None:
        """Increment a counter metric"""
        self.counters[metric] += value
    
    def record_request(self, tool: str, response_time: float, success: bool) -> None:
        """Record a request with its response time"""
        now = time.time()
        
        # Update counters
        self.counters['total_requests'] += 1
        if success:
            self.counters['successful_requests'] += 1
        else:
            self.counters['failed_requests'] += 1
        
        # Record response time
        self.request_times[tool].append(now)
        self.response_times[tool].append(response_time)
        
        # Track requests per minute
        current_minute = int(now / 60)
        if current_minute != self._last_minute:
            self.requests_per_minute.append(self._current_minute_requests)
            self._current_minute_requests = 1
            self._last_minute = current_minute
        else:
            self._current_minute_requests += 1
        
        # Log slow requests
        if response_time > 5.0:
            logger.warning(f"Slow request: {tool} took {response_time:.2f}s")
    
    def record_error(self, error_type: str, details: str = "") -> None:
        """Record an error occurrence"""
        self.errors[error_type] += 1
        self.last_errors.append({
            'type': error_type,
            'details': details[:200],  # Limit details length
            'timestamp': datetime.now().isoformat()
        })
    
    def get_summary(self) -> Dict[str, Any]:
        """Get metrics summary"""
        now = time.time()
        uptime = now - self.start_time
        
        # Calculate rates
        total_requests = self.counters['total_requests']
        success_rate = 0
        if total_requests > 0:
            success_rate = (self.counters['successful_requests'] / total_requests) * 100
        
        # Calculate average response times
        avg_response_times = {}
        for tool, times in self.response_times.items():
            if times:
                recent_times = times[-100:]  # Last 100 requests
                avg_response_times[tool] = {
                    'avg': sum(recent_times) / len(recent_times),
                    'min': min(recent_times),
                    'max': max(recent_times),
                    'count': len(times)
                }
        
        # Calculate current request rate
        rpm = sum(self.requests_per_minute) / max(1, len(self.requests_per_minute))
        
        return {
            'uptime_seconds': int(uptime),
            'uptime_formatted': self._format_uptime(uptime),
            'total_requests': total_requests,
            'successful_requests': self.counters['successful_requests'],
            'failed_requests': self.counters['failed_requests'],
            'success_rate': round(success_rate, 2),
            'requests_per_minute': round(rpm, 2),
            'rate_limited': self.counters.get('rate_limited', 0),
            'response_times': avg_response_times,
            'errors': dict(self.errors),
            'recent_errors': list(self.last_errors)[-10:],  # Last 10 errors
            'counters': dict(self.counters)
        }
    
    def _format_uptime(self, seconds: float) -> str:
        """Format uptime in human-readable format"""
        td = timedelta(seconds=int(seconds))
        days = td.days
        hours, remainder = divmod(td.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        parts = []
        if days:
            parts.append(f"{days}d")
        if hours:
            parts.append(f"{hours}h")
        if minutes:
            parts.append(f"{minutes}m")
        parts.append(f"{seconds}s")
        
        return " ".join(parts)
    
    def export_prometheus(self) -> str:
        """Export metrics in Prometheus format"""
        lines = []
        
        # Add help and type information
        lines.append("# HELP wordpress_mcp_requests_total Total number of requests")
        lines.append("# TYPE wordpress_mcp_requests_total counter")
        lines.append(f"wordpress_mcp_requests_total {self.counters['total_requests']}")
        
        lines.append("# HELP wordpress_mcp_requests_success Successful requests")
        lines.append("# TYPE wordpress_mcp_requests_success counter")
        lines.append(f"wordpress_mcp_requests_success {self.counters['successful_requests']}")
        
        lines.append("# HELP wordpress_mcp_requests_failed Failed requests")
        lines.append("# TYPE wordpress_mcp_requests_failed counter")
        lines.append(f"wordpress_mcp_requests_failed {self.counters['failed_requests']}")
        
        lines.append("# HELP wordpress_mcp_rate_limited Rate limited requests")
        lines.append("# TYPE wordpress_mcp_rate_limited counter")
        lines.append(f"wordpress_mcp_rate_limited {self.counters.get('rate_limited', 0)}")
        
        # Response times per tool
        for tool, times in self.response_times.items():
            if times:
                avg_time = sum(times[-100:]) / len(times[-100:])
                lines.append(f"# HELP wordpress_mcp_response_time_{tool} Average response time for {tool}")
                lines.append(f"# TYPE wordpress_mcp_response_time_{tool} gauge")
                lines.append(f"wordpress_mcp_response_time_{tool} {avg_time:.3f}")
        
        return "\n".join(lines)


class HealthChecker:
    """Health check management for the server"""
    
    def __init__(self):
        self.healthy = False
        self.last_check = None
        self.last_error = None
        self.start_time = time.time()
        self.checks_performed = 0
        self.checks_failed = 0
        
        # Component health
        self.components = {
            'wordpress_connection': False,
            'rate_limiter': True,
            'session_manager': True,
            'auth_manager': True
        }
    
    def set_healthy(self, healthy: bool, error: Optional[str] = None) -> None:
        """Set health status"""
        self.healthy = healthy
        self.last_check = datetime.now().isoformat()
        self.checks_performed += 1
        
        if not healthy:
            self.checks_failed += 1
            self.last_error = error
        else:
            self.last_error = None
        
        # Update WordPress connection component
        self.components['wordpress_connection'] = healthy
    
    def set_component_health(self, component: str, healthy: bool) -> None:
        """Set health status for a specific component"""
        if component in self.components:
            self.components[component] = healthy
    
    def is_healthy(self) -> bool:
        """Check if server is healthy"""
        # Overall health requires all components to be healthy
        return self.healthy and all(self.components.values())
    
    def get_uptime(self) -> float:
        """Get server uptime in seconds"""
        return time.time() - self.start_time
    
    def get_status(self) -> Dict[str, Any]:
        """Get detailed health status"""
        uptime = self.get_uptime()
        success_rate = 0
        if self.checks_performed > 0:
            success_rate = ((self.checks_performed - self.checks_failed) / 
                          self.checks_performed) * 100
        
        return {
            'status': 'healthy' if self.is_healthy() else 'unhealthy',
            'uptime_seconds': int(uptime),
            'last_check': self.last_check,
            'last_error': self.last_error,
            'checks_performed': self.checks_performed,
            'checks_failed': self.checks_failed,
            'success_rate': round(success_rate, 2),
            'components': self.components.copy(),
            'timestamp': datetime.now().isoformat()
        }
    
    async def run_health_checks(self, wp_client) -> bool:
        """Run comprehensive health checks"""
        all_healthy = True
        
        # Check WordPress connection
        try:
            wp_healthy = await wp_client.test_connection()
            self.components['wordpress_connection'] = wp_healthy
            if not wp_healthy:
                all_healthy = False
        except Exception as e:
            self.components['wordpress_connection'] = False
            all_healthy = False
            logger.error(f"WordPress health check failed: {e}")
        
        # Check other components (these are usually always healthy)
        # Could add more sophisticated checks here
        
        self.set_healthy(all_healthy)
        return all_healthy


class AlertManager:
    """Manages alerts and notifications"""
    
    def __init__(self, thresholds: Optional[Dict[str, Any]] = None):
        """
        Initialize alert manager
        
        Args:
            thresholds: Alert thresholds configuration
        """
        self.thresholds = thresholds or {
            'error_rate': 0.1,  # 10% error rate
            'response_time': 5.0,  # 5 seconds
            'rate_limit_hits': 100,  # 100 rate limit hits
            'memory_usage': 0.9  # 90% memory usage
        }
        
        self.active_alerts = {}
        self.alert_history = deque(maxlen=100)
    
    def check_alerts(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check metrics against thresholds and generate alerts"""
        alerts = []
        now = datetime.now()
        
        # Check error rate
        if metrics.get('total_requests', 0) > 100:  # Only after 100 requests
            error_rate = metrics.get('failed_requests', 0) / metrics['total_requests']
            if error_rate > self.thresholds['error_rate']:
                alerts.append(self._create_alert(
                    'high_error_rate',
                    'critical',
                    f"Error rate is {error_rate*100:.1f}%"
                ))
        
        # Check response times
        for tool, times in metrics.get('response_times', {}).items():
            if times.get('avg', 0) > self.thresholds['response_time']:
                alerts.append(self._create_alert(
                    'slow_response',
                    'warning',
                    f"{tool} average response time is {times['avg']:.2f}s"
                ))
        
        # Check rate limit hits
        rate_limited = metrics.get('rate_limited', 0)
        if rate_limited > self.thresholds['rate_limit_hits']:
            alerts.append(self._create_alert(
                'excessive_rate_limiting',
                'warning',
                f"Rate limited {rate_limited} requests"
            ))
        
        return alerts
    
    def _create_alert(self, alert_type: str, severity: str, message: str) -> Dict[str, Any]:
        """Create an alert object"""
        alert = {
            'type': alert_type,
            'severity': severity,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        
        # Track alert
        alert_key = f"{alert_type}:{severity}"
        self.active_alerts[alert_key] = alert
        self.alert_history.append(alert)
        
        # Log alert
        if severity == 'critical':
            logger.error(f"ALERT: {message}")
        else:
            logger.warning(f"Alert: {message}")
        
        return alert
    
    def clear_alert(self, alert_type: str, severity: str) -> None:
        """Clear an active alert"""
        alert_key = f"{alert_type}:{severity}"
        if alert_key in self.active_alerts:
            del self.active_alerts[alert_key]
    
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get all active alerts"""
        return list(self.active_alerts.values())
    
    def get_alert_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent alert history"""
        return list(self.alert_history)[-limit:]
