"""
Router Integration for Agent A
Handles communication with Vansh's Router service
"""

import requests
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

class RouterIntegration:
    """Integration with Vansh's Router service"""
    
    def __init__(self, router_url: str = "http://localhost:5000"):
        self.router_url = router_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Agent-A/1.0'
        })
    
    def send_offer(self, amount: float, description: str = "Agent A payment offer", 
                   metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Send offer to Router service
        
        Args:
            amount: Offer amount in ADA
            description: Payment description
            metadata: Additional metadata
            
        Returns:
            Router response
        """
        try:
            # Prepare offer payload
            offer_payload = {
                "from_agent": "agent_a",
                "to_agent": "agent_b",
                "amount": amount,
                "currency": "ADA",
                "description": description,
                "timestamp": datetime.now().isoformat() + "Z",
                "metadata": metadata or {
                    "arduino_trigger": True,
                    "button_type": "button_1",
                    "priority": "medium",
                    "agent_a_offer_id": str(uuid.uuid4())
                }
            }
            
            logger.info(f"Sending offer to Router: {offer_payload}")
            
            # Send to Router
            response = self.session.post(
                f"{self.router_url}/send_offer",
                json=offer_payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Router response: {result}")
                return {
                    "success": True,
                    "router_response": result,
                    "offer_payload": offer_payload
                }
            else:
                logger.error(f"Router error: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"Router error: {response.status_code}",
                    "details": response.text
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Router connection failed: {e}")
            return {
                "success": False,
                "error": f"Connection failed: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }
    
    def test_router_connection(self) -> bool:
        """Test connection to Router service"""
        try:
            # Try to reach Router health endpoint
            response = self.session.get(f"{self.router_url}/", timeout=10)
            return response.status_code == 200
        except:
            return False
    
    def get_router_status(self) -> Dict[str, Any]:
        """Get Router service status"""
        try:
            response = self.session.get(f"{self.router_url}/", timeout=10)
            return {
                "status": "connected",
                "code": response.status_code,
                "response": response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
            }
        except Exception as e:
            return {
                "status": "disconnected",
                "error": str(e)
            }
