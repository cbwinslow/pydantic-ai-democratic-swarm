"""Communication System for Agent Swarm.

Manages message passing and communication between agents in the swarm.
"""

import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime


logger = logging.getLogger(__name__)


@dataclass
class Message:
    """A message between agents."""
    sender: str
    recipient: str
    message_type: str
    content: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    message_id: str = ""


class SwarmCommunication:
    """Handles communication between agents in the swarm."""
    
    def __init__(self, swarm_name: str):
        """Initialize swarm communication.
        
        Args:
            swarm_name: Name of the swarm
        """
        self.swarm_name = swarm_name
        self.message_history: List[Message] = []
        self.logger = logging.getLogger(f"SwarmCommunication.{swarm_name}")
    
    async def send_message(
        self,
        sender: str,
        recipient: str,
        message_type: str,
        content: Dict[str, Any]
    ) -> bool:
        """Send a message from one agent to another.
        
        Args:
            sender: Sending agent name
            recipient: Receiving agent name
            message_type: Type of message
            content: Message content
            
        Returns:
            True if message sent successfully
        """
        message = Message(
            sender=sender,
            recipient=recipient,
            message_type=message_type,
            content=content,
            message_id=f"{sender}_{recipient}_{datetime.now().timestamp()}"
        )
        
        self.message_history.append(message)
        self.logger.debug(f"Message sent: {sender} -> {recipient} ({message_type})")
        
        return True
    
    async def broadcast_message(
        self,
        sender: str,
        message_type: str,
        content: Dict[str, Any],
        recipients: Optional[List[str]] = None
    ) -> int:
        """Broadcast a message to multiple agents.
        
        Args:
            sender: Sending agent name
            message_type: Type of message
            content: Message content
            recipients: List of recipients (None for all)
            
        Returns:
            Number of messages sent
        """
        if recipients is None:
            recipients = []  # Would get from swarm in real implementation
        
        count = 0
        for recipient in recipients:
            if await self.send_message(sender, recipient, message_type, content):
                count += 1
        
        return count
    
    def get_messages_for_agent(
        self,
        agent_name: str,
        since: Optional[datetime] = None
    ) -> List[Message]:
        """Get messages for a specific agent.
        
        Args:
            agent_name: Agent name
            since: Only return messages after this time
            
        Returns:
            List of messages for the agent
        """
        messages = [
            msg for msg in self.message_history
            if msg.recipient == agent_name
        ]
        
        if since:
            messages = [msg for msg in messages if msg.timestamp > since]
        
        return messages
    
    def get_communication_stats(self) -> Dict[str, Any]:
        """Get communication statistics.
        
        Returns:
            Dictionary with stats
        """
        return {
            "total_messages": len(self.message_history),
            "unique_senders": len(set(msg.sender for msg in self.message_history)),
            "unique_recipients": len(set(msg.recipient for msg in self.message_history)),
            "message_types": len(set(msg.message_type for msg in self.message_history))
        }
