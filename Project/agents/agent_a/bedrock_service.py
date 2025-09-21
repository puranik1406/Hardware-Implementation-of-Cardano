"""
AWS Bedrock service for Agent A decision-making
"""

import json
import logging
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
import boto3
from botocore.exceptions import ClientError

from .config import config
from .schemas import TriggerRequest, DecisionRequest

logger = logging.getLogger(__name__)

class BedrockService:
    """Service for AWS Bedrock integration with fallback logic"""
    
    def __init__(self):
        self.use_mock = config.USE_MOCK_BEDROCK
        self.bedrock_client = None
        
        if not self.use_mock:
            try:
                # Initialize both bedrock-runtime and bedrock-agent-runtime clients
                self.bedrock_client = boto3.client(
                    'bedrock-runtime',
                    region_name=config.AWS_REGION,
                    aws_access_key_id=config.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY
                )
                self.bedrock_agent_client = boto3.client(
                    'bedrock-agent-runtime',
                    region_name=config.AWS_REGION,
                    aws_access_key_id=config.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY
                )
                logger.info("AWS Bedrock clients initialized successfully")
                logger.info(f"Using Bedrock Agent ID: {config.BEDROCK_MODEL_ID}")
            except Exception as e:
                logger.warning(f"Failed to initialize Bedrock clients: {e}")
                self.use_mock = True
    
    def create_offer_decision(self, trigger: TriggerRequest) -> Dict[str, Any]:
        """Create offer decision using Bedrock or fallback logic"""
        
        if self.use_mock:
            return self._mock_offer_decision(trigger)
        
        try:
            return self._bedrock_offer_decision(trigger)
        except Exception as e:
            logger.error(f"Bedrock decision failed: {e}")
            return self._fallback_offer_decision(trigger)
    
    def evaluate_counter_offer(self, decision_req: DecisionRequest) -> Dict[str, Any]:
        """Evaluate counter offer using Bedrock or fallback logic"""
        
        if self.use_mock:
            return self._mock_counter_offer_decision(decision_req)
        
        try:
            return self._bedrock_counter_offer_decision(decision_req)
        except Exception as e:
            logger.error(f"Bedrock counter-offer evaluation failed: {e}")
            return self._fallback_counter_offer_decision(decision_req)
    
    def _mock_offer_decision(self, trigger: TriggerRequest) -> Dict[str, Any]:
        """Mock offer decision for testing"""
        amount = trigger.amount or config.FALLBACK_THRESHOLD
        
        # Mock logic: accept if amount is reasonable
        if amount >= config.MIN_OFFER_AMOUNT and amount <= config.MAX_OFFER_AMOUNT:
            status = "accepted"
            reason = f"Mock decision - offer accepted for testing (amount: {amount})"
        else:
            status = "rejected"
            reason = f"Mock decision - offer rejected (amount {amount} outside valid range)"
        
        return {
            "status": status,
            "amount": amount,
            "offer_id": str(uuid.uuid4()),
            "decision_reason": reason,
            "timestamp": datetime.now().isoformat(),
            "agent_id": "agent_a"
        }
    
    def _mock_counter_offer_decision(self, decision_req: DecisionRequest) -> Dict[str, Any]:
        """Mock counter offer decision for testing"""
        counter_amount = decision_req.counter_offer.get('amount', 0) if decision_req.counter_offer else 0
        
        if counter_amount >= config.MIN_OFFER_AMOUNT and counter_amount <= config.MAX_OFFER_AMOUNT:
            status = "accepted"
            reason = f"Mock decision - counter offer accepted (amount: {counter_amount})"
        else:
            status = "rejected"
            reason = f"Mock decision - counter offer rejected (amount {counter_amount} outside valid range)"
        
        return {
            "status": status,
            "amount": counter_amount,
            "offer_id": decision_req.offer_id,
            "decision_reason": reason,
            "timestamp": datetime.now().isoformat(),
            "agent_id": "agent_a"
        }
    
    def _bedrock_offer_decision(self, trigger: TriggerRequest) -> Dict[str, Any]:
        """Use AWS Bedrock Agent for offer decision"""
        prompt = self._create_offer_prompt(trigger)
        
        try:
            logger.info(f"Calling Bedrock Agent {config.BEDROCK_MODEL_ID} with prompt")
            logger.debug(f"Prompt: {prompt[:200]}...")
            
            # Call Bedrock Agent API
            response = self.bedrock_agent_client.invoke_agent(
                agentId=config.BEDROCK_MODEL_ID,
                agentAliasId='TSTALIASID',  # Use test alias as shown in console
                sessionId=str(uuid.uuid4()),
                inputText=prompt
            )
            
            # Extract response from event stream
            decision_text = ""
            for event in response['completion']:
                if 'chunk' in event:
                    chunk = event['chunk']
                    if 'bytes' in chunk:
                        decision_text += chunk['bytes'].decode('utf-8')
            
            logger.info(f"Raw Bedrock Agent response: {decision_text}")
            
            # Parse JSON response from Bedrock Agent
            try:
                # Try to extract JSON from response
                json_start = decision_text.find('{')
                json_end = decision_text.rfind('}') + 1
                
                if json_start >= 0 and json_end > json_start:
                    json_text = decision_text[json_start:json_end]
                    decision = json.loads(json_text)
                else:
                    # If no JSON found, create structured response
                    decision = self._parse_text_response(decision_text, trigger)
                
                # Validate and ensure required fields
                decision = self._validate_and_fix_decision(decision, trigger)
                
                logger.info(f"Parsed Bedrock Agent decision: {decision}")
                return decision
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse Bedrock Agent JSON response: {e}")
                logger.error(f"Raw response: {decision_text}")
                # Try to parse as text response
                return self._parse_text_response(decision_text, trigger)
                
        except ClientError as e:
            logger.error(f"AWS Bedrock Agent client error: {e}")
            return self._fallback_offer_decision(trigger)
        except Exception as e:
            logger.error(f"Unexpected error in Bedrock Agent call: {e}")
            return self._fallback_offer_decision(trigger)
    
    def _bedrock_counter_offer_decision(self, decision_req: DecisionRequest) -> Dict[str, Any]:
        """Use AWS Bedrock for counter offer decision"""
        prompt = self._create_counter_offer_prompt(decision_req)
        
        try:
            response = self.bedrock_client.invoke_model(
                modelId=config.BEDROCK_MODEL_ID,
                body=json.dumps({
                    "prompt": prompt,
                    "max_tokens_to_sample": 500,
                    "temperature": 0.7,
                    "top_p": 0.9
                })
            )
            
            response_body = json.loads(response['body'].read())
            decision_text = response_body['completion']
            
            logger.info(f"Raw Bedrock counter-offer response: {decision_text}")
            
            try:
                decision = json.loads(decision_text.strip())
                
                # Validate required fields
                required_fields = ['status', 'amount', 'offer_id', 'decision_reason', 'timestamp']
                for field in required_fields:
                    if field not in decision:
                        raise ValueError(f"Missing required field: {field}")
                
                # Add agent_id
                decision['agent_id'] = 'agent_a'
                
                logger.info(f"Parsed Bedrock counter-offer decision: {decision}")
                return decision
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse Bedrock JSON response: {e}")
                logger.error(f"Raw response: {decision_text}")
                return self._fallback_counter_offer_decision(decision_req)
                
        except ClientError as e:
            logger.error(f"AWS Bedrock client error: {e}")
            return self._fallback_counter_offer_decision(decision_req)
        except Exception as e:
            logger.error(f"Unexpected error in Bedrock call: {e}")
            return self._fallback_counter_offer_decision(decision_req)
    
    def _fallback_offer_decision(self, trigger: TriggerRequest) -> Dict[str, Any]:
        """Fallback rule-based offer decision"""
        amount = trigger.amount or config.FALLBACK_THRESHOLD
        
        # Rule-based logic
        if amount >= config.MIN_OFFER_AMOUNT and amount <= config.MAX_OFFER_AMOUNT:
            status = "accepted"
            reason = f"Fallback rule: amount {amount} within valid range ({config.MIN_OFFER_AMOUNT}-{config.MAX_OFFER_AMOUNT})"
        else:
            status = "rejected"
            reason = f"Fallback rule: amount {amount} outside valid range ({config.MIN_OFFER_AMOUNT}-{config.MAX_OFFER_AMOUNT})"
        
        return {
            "status": status,
            "amount": amount,
            "offer_id": str(uuid.uuid4()),
            "decision_reason": reason,
            "timestamp": datetime.now().isoformat(),
            "agent_id": "agent_a"
        }
    
    def _fallback_counter_offer_decision(self, decision_req: DecisionRequest) -> Dict[str, Any]:
        """Fallback rule-based counter offer decision"""
        counter_amount = decision_req.counter_offer.get('amount', 0) if decision_req.counter_offer else 0
        
        if counter_amount >= config.MIN_OFFER_AMOUNT and counter_amount <= config.MAX_OFFER_AMOUNT:
            status = "accepted"
            reason = f"Fallback rule: counter offer amount {counter_amount} within valid range"
        else:
            status = "rejected"
            reason = f"Fallback rule: counter offer amount {counter_amount} outside valid range"
        
        return {
            "status": status,
            "amount": counter_amount,
            "offer_id": decision_req.offer_id,
            "decision_reason": reason,
            "timestamp": datetime.now().isoformat(),
            "agent_id": "agent_a"
        }
    
    def _create_offer_prompt(self, trigger: TriggerRequest) -> str:
        """Create structured prompt for offer decision"""
        return f"""
You are Agent A, a buyer AI agent in a blockchain payment system. You need to decide whether to create an offer.

Context:
- Trigger type: {trigger.trigger_type}
- Suggested amount: {trigger.amount} lovelace
- Additional context: {trigger.context}
- Source: {trigger.source}

Rules:
- Valid amount range: {config.MIN_OFFER_AMOUNT} - {config.MAX_OFFER_AMOUNT} lovelace
- Consider if this is a reasonable test transaction
- Evaluate the trigger context for appropriateness

Please respond with a JSON object in this exact format:
{{
    "status": "accepted" or "rejected",
    "amount": <number in lovelace>,
    "offer_id": "<uuid>",
    "decision_reason": "<explanation>",
    "timestamp": "<ISO timestamp>"
}}

Consider:
- Is the amount reasonable for a test transaction?
- Does the trigger context make sense?
- Would this be a good test of the payment system?

Respond with ONLY the JSON object, no other text.
"""
    
    def _create_counter_offer_prompt(self, decision_req: DecisionRequest) -> str:
        """Create structured prompt for counter offer decision"""
        return f"""
You are Agent A, a buyer AI agent. You need to evaluate a counter offer.

Context:
- Original offer ID: {decision_req.offer_id}
- Counter offer: {decision_req.counter_offer}
- Agent B response: {decision_req.agent_b_response}
- Additional context: {decision_req.context}

Rules:
- Valid amount range: {config.MIN_OFFER_AMOUNT} - {config.MAX_OFFER_AMOUNT} lovelace
- Consider if the counter offer is reasonable
- Evaluate if you should accept or reject

Please respond with a JSON object in this exact format:
{{
    "status": "accepted" or "rejected",
    "amount": <final amount in lovelace>,
    "offer_id": "<original offer id>",
    "decision_reason": "<explanation>",
    "timestamp": "<ISO timestamp>"
}}

Consider:
- Is the counter offer reasonable?
- Does it meet your buying criteria?
- Would you accept this counter offer?

Respond with ONLY the JSON object, no other text.
"""

