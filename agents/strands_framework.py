"""
Strands Agent Framework — for the Fundamental Agent System
A framework where multiple agents collaborate on complex tasks
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
from datetime import datetime
from .deepseek_provider import DeepSeekProvider

class StrandStatus(Enum):
    """Strand execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class MessageType(Enum):
    """Message type"""
    DATA_REQUEST = "data_request"
    DATA_RESPONSE = "data_response"
    TASK_ASSIGNMENT = "task_assignment"
    TASK_COMPLETION = "task_completion"
    ERROR_NOTIFICATION = "error_notification"
    STATUS_UPDATE = "status_update"

@dataclass
class StrandMessage:
    """Message between agents"""
    sender: str
    receiver: str
    message_type: MessageType
    content: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    correlation_id: Optional[str] = None

@dataclass
class StrandContext:
    """Strand execution context"""
    strand_id: str
    input_data: Dict[str, Any]
    shared_memory: Dict[str, Any] = field(default_factory=dict)
    messages: List[StrandMessage] = field(default_factory=list)
    status: StrandStatus = StrandStatus.PENDING
    results: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)

class BaseStrandAgent(ABC):
    """Base class for Strand Agents"""
    
    def __init__(self, agent_id: str, name: str, model_id: str = "deepseek-v4-flash"):
        self.agent_id = agent_id
        self.name = name
        self.model_id = model_id
        self.logger = logging.getLogger(f"strand_agent.{agent_id}")
        self.dependencies: List[str] = []
        self.capabilities: List[str] = []
        
        # Initialize DeepSeek API client
        try:
            self.llm = DeepSeekProvider(
                model=model_id,
                temperature=0.7,
                max_tokens=4000
            )
            self.logger.info(f"✅ {name} Agent initialized")
        except Exception as e:
            self.logger.error(f"❌ {name} Agent initialization failed: {e}")
            self.llm = None
    
    @abstractmethod
    async def process(self, context: StrandContext, message: Optional[StrandMessage] = None) -> Dict[str, Any]:
        """Main processing logic for the agent"""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """Return list of agent capabilities"""
        pass
    
    async def send_message(self, context: StrandContext, receiver: str, message_type: MessageType, content: Dict[str, Any]):
        """Send message to another agent"""
        message = StrandMessage(
            sender=self.agent_id,
            receiver=receiver,
            message_type=message_type,
            content=content,
            correlation_id=context.strand_id
        )
        context.messages.append(message)
        self.logger.info(f"📤 Message sent: {self.agent_id} -> {receiver} ({message_type.value})")
    
    async def get_shared_data(self, context: StrandContext, key: str) -> Any:
        """Retrieve data from shared memory"""
        return context.shared_memory.get(key)
    
    async def set_shared_data(self, context: StrandContext, key: str, value: Any):
        """Store data in shared memory"""
        context.shared_memory[key] = value
        self.logger.debug(f"💾 Shared data saved: {key}")
    
    async def call_llm(self, system_prompt: str, user_prompt: str) -> str:
        """Call LLM"""
        if not self.llm:
            raise Exception("LLM not initialized")
        
        try:
            # Call DeepSeekProvider.ainvoke(system_prompt, user_prompt)
            response = await self.llm.ainvoke(system_prompt, user_prompt)
            return response
        except Exception as e:
            self.logger.error(f"❌ LLM call failed: {e}")
            raise

class StrandOrchestrator:
    """Strand Orchestrator — coordinates agent collaboration"""
    
    def __init__(self):
        self.agents: Dict[str, BaseStrandAgent] = {}
        self.logger = logging.getLogger("strand_orchestrator")
        self.active_strands: Dict[str, StrandContext] = {}
    
    def register_agent(self, agent: BaseStrandAgent):
        """Register agent"""
        self.agents[agent.agent_id] = agent
        self.logger.info(f"🤖 Agent registered: {agent.name} ({agent.agent_id})")
    
    async def execute_strand(self, strand_id: str, input_data: Dict[str, Any], workflow: List[str]) -> StrandContext:
        """Execute strand"""
        context = StrandContext(
            strand_id=strand_id,
            input_data=input_data,
            status=StrandStatus.RUNNING
        )
        
        self.active_strands[strand_id] = context
        self.logger.info(f"🚀 Strand execution started: {strand_id}")
        
        try:
            # 워크플로우에 따라 에이전트들을 순차적으로 실행
            for agent_id in workflow:
                if agent_id not in self.agents:
                    raise Exception(f"Agent not found: {agent_id}")
                
                agent = self.agents[agent_id]
                self.logger.info(f"🔄 Agent executing: {agent.name}")
                
                # Execute agent
                result = await agent.process(context)
                context.results[agent_id] = result
                
                # Status update
                await agent.set_shared_data(context, f"{agent_id}_result", result)
            
            context.status = StrandStatus.COMPLETED
            self.logger.info(f"✅ Strand execution completed: {strand_id}")
            
        except Exception as e:
            context.status = StrandStatus.FAILED
            context.error = str(e)
            self.logger.error(f"❌ Strand execution failed: {strand_id} - {e}")
        
        return context
    
    async def get_strand_status(self, strand_id: str) -> Optional[StrandContext]:
        """Query strand status"""
        return self.active_strands.get(strand_id)
    
    def list_agents(self) -> Dict[str, List[str]]:
        """List registered agents and their capabilities"""
        return {
            agent_id: agent.get_capabilities() 
            for agent_id, agent in self.agents.items()
        }

# Global orchestrator instance
orchestrator = StrandOrchestrator()
