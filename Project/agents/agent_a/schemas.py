"""
Pydantic schemas for Agent A API
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
from datetime import datetime
import uuid

class TriggerRequest(BaseModel):
    """Request model for trigger input from Arduino/Router"""
    trigger_type: str = Field(..., description="Type of trigger (arduino, manual, scheduled)")
    amount: Optional[float] = Field(None, description="Suggested amount for offer in lovelace")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context data")
    timestamp: Optional[str] = Field(None, description="Trigger timestamp")
    source: Optional[str] = Field(None, description="Source of the trigger (arduino_a, manual, etc.)")
    
    @validator('amount')
    def validate_amount(cls, v):
        if v is not None and v < 0:
            raise ValueError('Amount must be positive')
        return v

class OfferResponse(BaseModel):
    """Response model for offer creation"""
    status: str = Field(..., description="Status of the offer (accepted, rejected, pending)")
    amount: float = Field(..., description="Offer amount in lovelace")
    offer_id: str = Field(..., description="Unique offer identifier")
    decision_reason: str = Field(..., description="Reason for the decision")
    timestamp: str = Field(..., description="Offer creation timestamp")
    transaction_hash: Optional[str] = Field(None, description="Blockchain transaction hash")
    agent_id: str = Field(default="agent_a", description="ID of the agent making the offer")
    
    @validator('status')
    def validate_status(cls, v):
        allowed_statuses = ['accepted', 'rejected', 'pending']
        if v not in allowed_statuses:
            raise ValueError(f'Status must be one of {allowed_statuses}')
        return v

class DecisionRequest(BaseModel):
    """Request model for decision evaluation"""
    offer_id: str = Field(..., description="Offer ID to evaluate")
    counter_offer: Optional[Dict[str, Any]] = Field(None, description="Counter offer details")
    context: Optional[Dict[str, Any]] = Field(None, description="Decision context")
    agent_b_response: Optional[Dict[str, Any]] = Field(None, description="Response from Agent B")
    
    @validator('offer_id')
    def validate_offer_id(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Offer ID cannot be empty')
        return v

class DecisionResponse(BaseModel):
    """Response model for decision evaluation"""
    status: str = Field(..., description="Decision status (accepted, rejected)")
    amount: float = Field(..., description="Final agreed amount in lovelace")
    offer_id: str = Field(..., description="Offer identifier")
    decision_reason: str = Field(..., description="Reason for decision")
    timestamp: str = Field(..., description="Decision timestamp")
    agent_id: str = Field(default="agent_a", description="ID of the agent making the decision")
    transaction_details: Optional[Dict[str, Any]] = Field(None, description="Transaction details if accepted")
    
    @validator('status')
    def validate_status(cls, v):
        allowed_statuses = ['accepted', 'rejected']
        if v not in allowed_statuses:
            raise ValueError(f'Status must be one of {allowed_statuses}')
        return v

class HealthResponse(BaseModel):
    """Health check response model"""
    service: str = Field(..., description="Service name")
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="Service version")
    bedrock_mode: str = Field(..., description="Bedrock mode (mock/real)")
    uptime: Optional[str] = Field(None, description="Service uptime")
    last_offer_id: Optional[str] = Field(None, description="Last processed offer ID")

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Error details")
    timestamp: str = Field(..., description="Error timestamp")
    request_id: Optional[str] = Field(None, description="Request ID for tracking")

# Offer JSON Schema for coordination with Router (Vansh)
OFFER_SCHEMA = {
    "type": "object",
    "properties": {
        "offer_id": {"type": "string", "format": "uuid"},
        "agent_id": {"type": "string", "enum": ["agent_a", "agent_b"]},
        "amount": {"type": "number", "minimum": 100000, "maximum": 10000000},
        "status": {"type": "string", "enum": ["accepted", "rejected", "pending"]},
        "decision_reason": {"type": "string"},
        "timestamp": {"type": "string", "format": "date-time"},
        "transaction_hash": {"type": ["string", "null"]},
        "context": {"type": "object"}
    },
    "required": ["offer_id", "agent_id", "amount", "status", "decision_reason", "timestamp"]
}

# Decision JSON Schema for coordination with Router
DECISION_SCHEMA = {
    "type": "object",
    "properties": {
        "offer_id": {"type": "string", "format": "uuid"},
        "agent_id": {"type": "string", "enum": ["agent_a", "agent_b"]},
        "status": {"type": "string", "enum": ["accepted", "rejected"]},
        "amount": {"type": "number", "minimum": 100000, "maximum": 10000000},
        "decision_reason": {"type": "string"},
        "timestamp": {"type": "string", "format": "date-time"},
        "transaction_details": {"type": "object"}
    },
    "required": ["offer_id", "agent_id", "status", "amount", "decision_reason", "timestamp"]
}

