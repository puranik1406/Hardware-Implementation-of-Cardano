"""
Production Monitoring Dashboard for Agent A
Real-time monitoring and alerting system
"""

from flask import Flask, render_template, jsonify, request
import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List
import logging
from metrics_collector import metrics_collector
from logging_config import structured_logger

app = Flask(__name__)

class MonitoringDashboard:
    """Real-time monitoring dashboard for Agent A"""
    
    def __init__(self):
        self.alerts = []
        self.alert_thresholds = {
            "cpu_percent": 80,
            "memory_percent": 85,
            "error_rate": 10,
            "response_time_ms": 5000
        }
        self.start_monitoring()
    
    def start_monitoring(self):
        """Start background monitoring"""
        # Start metrics collection
        metrics_collector.start_collection()
        
        # Start alert monitoring
        alert_thread = threading.Thread(target=self._monitor_alerts, daemon=True)
        alert_thread.start()
    
    def _monitor_alerts(self):
        """Monitor for alert conditions"""
        while True:
            try:
                self._check_alerts()
                time.sleep(30)  # Check every 30 seconds
            except Exception as e:
                logging.error(f"Alert monitoring error: {e}")
                time.sleep(30)
    
    def _check_alerts(self):
        """Check for alert conditions"""
        current_metrics = metrics_collector.collect_current_metrics()
        
        if 'system' in current_metrics:
            system = current_metrics['system']
            
            # CPU alert
            if system['cpu_percent'] > self.alert_thresholds['cpu_percent']:
                self._create_alert("HIGH_CPU", f"CPU usage is {system['cpu_percent']}%", "warning")
            
            # Memory alert
            if system['memory']['percent'] > self.alert_thresholds['memory_percent']:
                self._create_alert("HIGH_MEMORY", f"Memory usage is {system['memory']['percent']}%", "warning")
        
        if 'application' in current_metrics:
            app_metrics = current_metrics['application']
            
            # Error rate alert
            if app_metrics['api_requests']['total'] > 0:
                error_rate = (app_metrics['api_requests']['errors'] / app_metrics['api_requests']['total']) * 100
                if error_rate > self.alert_thresholds['error_rate']:
                    self._create_alert("HIGH_ERROR_RATE", f"Error rate is {error_rate:.1f}%", "critical")
    
    def _create_alert(self, alert_type: str, message: str, severity: str):
        """Create a new alert"""
        alert = {
            "id": f"{alert_type}_{int(time.time())}",
            "type": alert_type,
            "message": message,
            "severity": severity,
            "timestamp": datetime.now().isoformat(),
            "acknowledged": False
        }
        
        # Avoid duplicate alerts
        if not any(a['type'] == alert_type and not a['acknowledged'] for a in self.alerts):
            self.alerts.append(alert)
            structured_logger.log_system_metrics(0, 0, 0, 0)  # Log alert
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get dashboard data"""
        current_metrics = metrics_collector.collect_current_metrics()
        summary = metrics_collector.get_metrics_summary(hours=1)
        
        # Get recent alerts
        recent_alerts = [a for a in self.alerts if not a['acknowledged']]
        
        return {
            "current_metrics": current_metrics,
            "summary": summary,
            "alerts": recent_alerts,
            "timestamp": datetime.now().isoformat()
        }

# Initialize dashboard
dashboard = MonitoringDashboard()

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/metrics')
def get_metrics():
    """Get current metrics"""
    return jsonify(dashboard.get_dashboard_data())

@app.route('/api/alerts')
def get_alerts():
    """Get alerts"""
    return jsonify(dashboard.alerts)

@app.route('/api/alerts/<alert_id>/acknowledge', methods=['POST'])
def acknowledge_alert(alert_id):
    """Acknowledge an alert"""
    for alert in dashboard.alerts:
        if alert['id'] == alert_id:
            alert['acknowledged'] = True
            return jsonify({"status": "acknowledged"})
    
    return jsonify({"error": "Alert not found"}), 404

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    try:
        # Check if Agent A is responding
        import requests
        response = requests.get('http://localhost:8001/', timeout=5)
        
        return jsonify({
            "status": "healthy",
            "agent_a_status": "connected" if response.status_code == 200 else "disconnected",
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/logs')
def get_logs():
    """Get recent logs"""
    try:
        # Read recent logs from file
        with open('logs/agent_a.log', 'r') as f:
            lines = f.readlines()
            recent_lines = lines[-100:]  # Last 100 lines
        
        return jsonify({
            "logs": recent_lines,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)
