"""
Production Logging Configuration for Agent A
"""

import logging
import logging.handlers
import json
import os
from datetime import datetime
from typing import Dict, Any

class StructuredLogger:
    """Structured logging for production monitoring"""
    
    def __init__(self, service_name: str = "agent_a", log_level: str = "INFO"):
        self.service_name = service_name
        self.log_level = getattr(logging, log_level.upper())
        self.setup_logging()
    
    def setup_logging(self):
        """Setup production logging configuration"""
        
        # Create logs directory
        os.makedirs('logs', exist_ok=True)
        
        # Configure root logger
        logger = logging.getLogger()
        logger.setLevel(self.log_level)
        
        # Clear existing handlers
        logger.handlers.clear()
        
        # Console handler for development
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_format)
        logger.addHandler(console_handler)
        
        # File handler for all logs
        file_handler = logging.handlers.RotatingFileHandler(
            'logs/agent_a.log',
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)
        
        # Error handler for errors only
        error_handler = logging.handlers.RotatingFileHandler(
            'logs/agent_a_errors.log',
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_format)
        logger.addHandler(error_handler)
        
        # JSON handler for structured logs
        json_handler = logging.handlers.RotatingFileHandler(
            'logs/agent_a_structured.log',
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        json_handler.setLevel(logging.INFO)
        json_handler.setFormatter(JsonFormatter())
        logger.addHandler(json_handler)
    
    def log_api_request(self, method: str, endpoint: str, status_code: int, 
                       response_time: float, user_agent: str = None):
        """Log API request details"""
        logger = logging.getLogger('api')
        
        log_data = {
            "event_type": "api_request",
            "service": self.service_name,
            "method": method,
            "endpoint": endpoint,
            "status_code": status_code,
            "response_time_ms": round(response_time * 1000, 2),
            "user_agent": user_agent,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(json.dumps(log_data))
    
    def log_offer_creation(self, offer_id: str, amount: float, status: str, 
                          decision_reason: str, trigger_type: str):
        """Log offer creation events"""
        logger = logging.getLogger('offers')
        
        log_data = {
            "event_type": "offer_created",
            "service": self.service_name,
            "offer_id": offer_id,
            "amount_lovelace": amount,
            "amount_ada": amount / 1000000,
            "status": status,
            "decision_reason": decision_reason,
            "trigger_type": trigger_type,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(json.dumps(log_data))
    
    def log_router_integration(self, offer_id: str, router_response: Dict[str, Any], 
                              success: bool, error: str = None):
        """Log Router integration events"""
        logger = logging.getLogger('router')
        
        log_data = {
            "event_type": "router_integration",
            "service": self.service_name,
            "offer_id": offer_id,
            "success": success,
            "router_response": router_response,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        
        if success:
            logger.info(json.dumps(log_data))
        else:
            logger.error(json.dumps(log_data))
    
    def log_bedrock_usage(self, model_id: str, prompt_tokens: int, 
                         completion_tokens: int, response_time: float, 
                         success: bool, error: str = None):
        """Log AWS Bedrock usage"""
        logger = logging.getLogger('bedrock')
        
        log_data = {
            "event_type": "bedrock_usage",
            "service": self.service_name,
            "model_id": model_id,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
            "response_time_ms": round(response_time * 1000, 2),
            "success": success,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        
        if success:
            logger.info(json.dumps(log_data))
        else:
            logger.error(json.dumps(log_data))
    
    def log_system_metrics(self, cpu_percent: float, memory_mb: float, 
                          active_connections: int, uptime_seconds: float):
        """Log system metrics"""
        logger = logging.getLogger('metrics')
        
        log_data = {
            "event_type": "system_metrics",
            "service": self.service_name,
            "cpu_percent": cpu_percent,
            "memory_mb": memory_mb,
            "active_connections": active_connections,
            "uptime_seconds": uptime_seconds,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(json.dumps(log_data))

class JsonFormatter(logging.Formatter):
    """JSON formatter for structured logs"""
    
    def format(self, record):
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry)

# Global logger instance
structured_logger = StructuredLogger()
