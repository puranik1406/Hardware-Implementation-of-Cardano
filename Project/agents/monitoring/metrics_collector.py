"""
Metrics Collector for Agent A Production Monitoring
"""

import psutil
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List
import json
import logging

logger = logging.getLogger(__name__)

class MetricsCollector:
    """Collect and store system and application metrics"""
    
    def __init__(self, collection_interval: int = 60):
        self.collection_interval = collection_interval
        self.metrics_history = []
        self.start_time = time.time()
        self.is_running = False
        self.collector_thread = None
        
        # Metrics counters
        self.api_requests_total = 0
        self.api_requests_success = 0
        self.api_requests_error = 0
        self.offers_created = 0
        self.offers_sent_to_router = 0
        self.router_errors = 0
        self.bedrock_requests = 0
        self.bedrock_errors = 0
    
    def start_collection(self):
        """Start metrics collection in background thread"""
        if not self.is_running:
            self.is_running = True
            self.collector_thread = threading.Thread(target=self._collect_metrics_loop, daemon=True)
            self.collector_thread.start()
            logger.info("Metrics collection started")
    
    def stop_collection(self):
        """Stop metrics collection"""
        self.is_running = False
        if self.collector_thread:
            self.collector_thread.join(timeout=5)
        logger.info("Metrics collection stopped")
    
    def _collect_metrics_loop(self):
        """Main metrics collection loop"""
        while self.is_running:
            try:
                metrics = self.collect_current_metrics()
                self.metrics_history.append(metrics)
                
                # Keep only last 24 hours of metrics (assuming 1-minute intervals)
                max_entries = 24 * 60
                if len(self.metrics_history) > max_entries:
                    self.metrics_history = self.metrics_history[-max_entries:]
                
                time.sleep(self.collection_interval)
            except Exception as e:
                logger.error(f"Error collecting metrics: {e}")
                time.sleep(self.collection_interval)
    
    def collect_current_metrics(self) -> Dict[str, Any]:
        """Collect current system and application metrics"""
        try:
            # System metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Network connections
            connections = len(psutil.net_connections())
            
            # Process metrics
            process = psutil.Process()
            process_memory = process.memory_info()
            process_cpu = process.cpu_percent()
            
            # Uptime
            uptime_seconds = time.time() - self.start_time
            
            # Application metrics
            success_rate = (self.api_requests_success / max(self.api_requests_total, 1)) * 100
            router_success_rate = ((self.offers_sent_to_router - self.router_errors) / max(self.offers_sent_to_router, 1)) * 100
            bedrock_success_rate = ((self.bedrock_requests - self.bedrock_errors) / max(self.bedrock_requests, 1)) * 100
            
            metrics = {
                "timestamp": datetime.now().isoformat(),
                "uptime_seconds": uptime_seconds,
                
                # System metrics
                "system": {
                    "cpu_percent": cpu_percent,
                    "memory": {
                        "total_mb": round(memory.total / 1024 / 1024, 2),
                        "available_mb": round(memory.available / 1024 / 1024, 2),
                        "used_mb": round(memory.used / 1024 / 1024, 2),
                        "percent": memory.percent
                    },
                    "disk": {
                        "total_gb": round(disk.total / 1024 / 1024 / 1024, 2),
                        "used_gb": round(disk.used / 1024 / 1024 / 1024, 2),
                        "free_gb": round(disk.free / 1024 / 1024 / 1024, 2),
                        "percent": round((disk.used / disk.total) * 100, 2)
                    },
                    "network_connections": connections
                },
                
                # Process metrics
                "process": {
                    "cpu_percent": process_cpu,
                    "memory_mb": round(process_memory.rss / 1024 / 1024, 2),
                    "memory_percent": round((process_memory.rss / memory.total) * 100, 2)
                },
                
                # Application metrics
                "application": {
                    "api_requests": {
                        "total": self.api_requests_total,
                        "success": self.api_requests_success,
                        "errors": self.api_requests_error,
                        "success_rate_percent": round(success_rate, 2)
                    },
                    "offers": {
                        "created": self.offers_created,
                        "sent_to_router": self.offers_sent_to_router,
                        "router_errors": self.router_errors,
                        "router_success_rate_percent": round(router_success_rate, 2)
                    },
                    "bedrock": {
                        "requests": self.bedrock_requests,
                        "errors": self.bedrock_errors,
                        "success_rate_percent": round(bedrock_success_rate, 2)
                    }
                }
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
    
    def increment_api_request(self, success: bool = True):
        """Increment API request counter"""
        self.api_requests_total += 1
        if success:
            self.api_requests_success += 1
        else:
            self.api_requests_error += 1
    
    def increment_offer_created(self):
        """Increment offer creation counter"""
        self.offers_created += 1
    
    def increment_router_send(self, success: bool = True):
        """Increment Router send counter"""
        self.offers_sent_to_router += 1
        if not success:
            self.router_errors += 1
    
    def increment_bedrock_request(self, success: bool = True):
        """Increment Bedrock request counter"""
        self.bedrock_requests += 1
        if not success:
            self.bedrock_errors += 1
    
    def get_metrics_summary(self, hours: int = 1) -> Dict[str, Any]:
        """Get metrics summary for the last N hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        recent_metrics = [
            m for m in self.metrics_history 
            if datetime.fromisoformat(m['timestamp']) >= cutoff_time
        ]
        
        if not recent_metrics:
            return {"error": "No metrics available for the specified time period"}
        
        # Calculate averages
        cpu_values = [m['system']['cpu_percent'] for m in recent_metrics if 'system' in m]
        memory_values = [m['system']['memory']['percent'] for m in recent_metrics if 'system' in m]
        
        summary = {
            "time_period_hours": hours,
            "metrics_count": len(recent_metrics),
            "averages": {
                "cpu_percent": round(sum(cpu_values) / len(cpu_values), 2) if cpu_values else 0,
                "memory_percent": round(sum(memory_values) / len(memory_values), 2) if memory_values else 0
            },
            "current_metrics": recent_metrics[-1] if recent_metrics else None,
            "timestamp": datetime.now().isoformat()
        }
        
        return summary
    
    def export_metrics(self, filepath: str = None) -> str:
        """Export metrics to JSON file"""
        if not filepath:
            filepath = f"metrics_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "collection_interval": self.collection_interval,
            "total_metrics": len(self.metrics_history),
            "metrics": self.metrics_history
        }
        
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        logger.info(f"Metrics exported to {filepath}")
        return filepath

# Global metrics collector instance
metrics_collector = MetricsCollector()
