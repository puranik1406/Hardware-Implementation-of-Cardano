# 🚀 Agent A Production Deployment Guide

## Overview
Complete production deployment setup for Agent A with monitoring, logging, and integration testing.

## 🏗️ Architecture

### Components
- **Agent A Service**: Main FastAPI service
- **Router Integration**: Communication with Vansh's Router service
- **Monitoring Dashboard**: Real-time metrics and alerts
- **Logging System**: Structured logging with rotation
- **Metrics Collection**: System and application metrics
- **Docker Deployment**: Containerized production setup

## 📋 Prerequisites

### System Requirements
- Docker & Docker Compose
- Python 3.11+
- 2GB RAM minimum
- 10GB disk space

### Dependencies
```bash
pip install -r requirements.txt
```

## 🚀 Quick Deployment

### Option 1: PowerShell (Windows)
```powershell
# Navigate to agents directory
cd C:\Users\H.P\project\agents

# Run deployment script
.\deploy.ps1

# Or with options
.\deploy.ps1 -Environment production -SkipTests:$false
```

### Option 2: Bash (Linux/Mac)
```bash
# Navigate to agents directory
cd agents

# Make script executable
chmod +x deploy.sh

# Run deployment
./deploy.sh
```

### Option 3: Manual Docker
```bash
# Build image
docker build -t agent-a:latest -f docker/Dockerfile .

# Run container
docker run -d \
  --name agent-a-service \
  -p 8001:8001 \
  -v $(pwd)/logs:/app/logs \
  agent-a:latest
```

## 🔧 Configuration

### Environment Variables
```bash
# Core Configuration
USE_MOCK_BEDROCK=true
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=8001

# Router Integration
ROUTER_URL=http://router:5000

# AWS Bedrock (Production)
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=us-east-1
USE_MOCK_BEDROCK=false

# Monitoring
METRICS_COLLECTION_INTERVAL=60
ALERT_CPU_THRESHOLD=80
ALERT_MEMORY_THRESHOLD=85
```

## 📊 Monitoring & Logging

### Monitoring Dashboard
- **URL**: http://localhost:5001
- **Features**: Real-time metrics, alerts, logs
- **Endpoints**:
  - `/api/metrics` - Current metrics
  - `/api/alerts` - Active alerts
  - `/api/health` - Health check
  - `/api/logs` - Recent logs

### Log Files
```
logs/
├── agent_a.log              # All logs
├── agent_a_errors.log       # Error logs only
├── agent_a_structured.log   # JSON structured logs
└── metrics_export_*.json    # Metrics exports
```

### Metrics Collected
- **System**: CPU, Memory, Disk, Network
- **Application**: API requests, Offers, Router integration
- **Bedrock**: Usage, errors, response times
- **Performance**: Response times, success rates

## 🧪 Testing

### Integration Tests
```bash
# Run comprehensive tests
python comprehensive_integration_tests.py

# Run specific test categories
python test_router_integration.py
python test_agent_a.py
```

### Test Coverage
- ✅ Agent A health checks
- ✅ Router connectivity
- ✅ Offer creation and processing
- ✅ Router integration flow
- ✅ Performance testing
- ✅ Error handling
- ✅ AWS Bedrock fallback

## 🔍 Troubleshooting

### Common Issues

#### Service Won't Start
```bash
# Check logs
docker logs agent-a-service

# Check port conflicts
netstat -tuln | grep :8001

# Restart service
docker restart agent-a-service
```

#### Router Connection Failed
```bash
# Check Router service
curl http://localhost:5000/

# Test Router integration
curl http://localhost:8001/agentA/router_status
```

#### High Resource Usage
```bash
# Check metrics
curl http://localhost:5001/api/metrics

# View logs
tail -f logs/agent_a.log
```

### Health Checks
```bash
# Agent A health
curl http://localhost:8001/

# Monitoring dashboard
curl http://localhost:5001/api/health

# Router status
curl http://localhost:8001/agentA/router_status
```

## 📈 Performance Optimization

### Production Settings
```python
# Gunicorn configuration
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"
max_requests = 1000
max_requests_jitter = 100
```

### Monitoring Alerts
- **CPU > 80%**: Warning alert
- **Memory > 85%**: Warning alert
- **Error Rate > 10%**: Critical alert
- **Response Time > 5s**: Warning alert

## 🔒 Security

### Production Security
- Non-root container user
- Health check endpoints
- Structured logging (no sensitive data)
- Environment variable configuration
- Network isolation

### Monitoring Security
- Dashboard access control
- Log rotation and retention
- Alert acknowledgment system
- Metrics export controls

## 📋 Maintenance

### Daily Tasks
- Check monitoring dashboard
- Review error logs
- Monitor resource usage
- Verify Router connectivity

### Weekly Tasks
- Export metrics for analysis
- Review performance trends
- Update dependencies
- Test integration flows

### Monthly Tasks
- Security updates
- Performance optimization
- Capacity planning
- Backup verification

## 🚨 Alerts & Notifications

### Alert Types
- **HIGH_CPU**: CPU usage above threshold
- **HIGH_MEMORY**: Memory usage above threshold
- **HIGH_ERROR_RATE**: API error rate above threshold
- **ROUTER_DISCONNECTED**: Router service unavailable
- **BEDROCK_ERROR**: AWS Bedrock service issues

### Alert Management
```bash
# View active alerts
curl http://localhost:5001/api/alerts

# Acknowledge alert
curl -X POST http://localhost:5001/api/alerts/{alert_id}/acknowledge
```

## 📞 Support

### Logs Location
- Application logs: `logs/agent_a.log`
- Error logs: `logs/agent_a_errors.log`
- Structured logs: `logs/agent_a_structured.log`

### Metrics Export
```bash
# Export metrics
python -c "from monitoring.metrics_collector import metrics_collector; metrics_collector.export_metrics()"
```

### Service URLs
- **Agent A**: http://localhost:8001
- **API Docs**: http://localhost:8001/docs
- **Monitoring**: http://localhost:5001
- **Health Check**: http://localhost:8001/

## 🎯 Success Metrics

### Key Performance Indicators
- **Uptime**: > 99.9%
- **Response Time**: < 2 seconds
- **Error Rate**: < 1%
- **Router Integration**: > 99% success
- **Bedrock Availability**: > 95%

### Monitoring Checklist
- [ ] Service is running
- [ ] Health checks passing
- [ ] Router connectivity
- [ ] Metrics collection active
- [ ] No critical alerts
- [ ] Log rotation working
- [ ] Alerts configured
- [ ] Dashboard accessible
