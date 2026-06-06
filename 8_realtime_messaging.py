"""
Real-time Messaging — WebSocket connections, message queue, presence tracking
Powers Messenger app with real-time delivery and read receipts.
"""

import time
import uuid
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class Message:
    id: str
    sender_id: str
    recipient_id: str
    text: str
    timestamp: float
    delivered: bool = False
    read: bool = False


@dataclass
class Conversation:
    id: str
    participants: List[str]
    is_group: bool
    name: Optional[str] = None
    created_at: float = None
    messages: List[Message] = None
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = time.time()
        if not self.messages:
            self.messages = []


class WebSocketServer:
    """Simulates WebSocket server for real-time connections."""

    def __init__(self):
        self.connections: Dict[str, str] = {}  # user_id -> device
        self.presence: Dict[str, float] = {}  # user_id -> last_active

    def connect(self, user_id: str, device: str):
        """User connects via WebSocket."""
        self.connections[user_id] = device
        self.presence[user_id] = time.time()

    def disconnect(self, user_id: str):
        """User disconnects."""
        if user_id in self.connections:
            del self.connections[user_id]

    def is_online(self, user_id: str) -> bool:
        """Check if user is online."""
        return user_id in self.connections

    def active_users(self) -> List[str]:
        """Get list of active users."""
        return list(self.connections.keys())


class MessageStore:
    """Stores messages and conversations."""

    def __init__(self):
        self.conversations: Dict[str, Conversation] = {}  # conv_id -> conv
        self.user_conversations: Dict[str, Set[str]] = defaultdict(set)  # user_id -> conv_ids
        self.message_queue: List[Message] = []  # Outgoing message queue

    def create_conversation(self, participants: List[str], is_group: bool = False, name: Optional[str] = None) -> Conversation:
        """Create a new conversation."""
        conv_id = str(uuid.uuid4())[:8]
        conv = Conversation(
            id=conv_id,
            participants=participants,
            is_group=is_group,
            name=name
        )
        self.conversations[conv_id] = conv
        
        # Add to each user's conversations
        for participant in participants:
            self.user_conversations[participant].add(conv_id)
        
        return conv

    def add_message(self, message: Message):
        """Add a message to store and queue."""
        self.message_queue.append(message)

    def get_conversation(self, conv_id: str) -> Optional[Conversation]:
        """Retrieve a conversation."""
        return self.conversations.get(conv_id)


class MessengerService:
    """Main Messenger service tying together WebSocket and message store."""

    def __init__(self):
        self.ws = WebSocketServer()
        self.store = MessageStore()

    def send_message(self, sender_id: str, recipient_id: str, text: str) -> Message:
        """Send a one-on-one message."""
        msg_id = str(uuid.uuid4())[:8]
        message = Message(
            id=msg_id,
            sender_id=sender_id,
            recipient_id=recipient_id,
            text=text,
            timestamp=time.time(),
            delivered=self.ws.is_online(recipient_id)
        )
        self.store.add_message(message)
        return message

    def send_group_message(self, sender_id: str, conv_id: str, text: str) -> Message:
        """Send a message to a group conversation."""
        conv = self.store.get_conversation(conv_id)
        if not conv:
            return None
        
        msg_id = str(uuid.uuid4())[:8]
        message = Message(
            id=msg_id,
            sender_id=sender_id,
            recipient_id=conv_id,  # recipient_id = conv_id for groups
            text=text,
            timestamp=time.time(),
            delivered=True  # Mark group messages as delivered immediately
        )
        conv.messages.append(message)
        self.store.add_message(message)
        return message

    def process_queue(self) -> Dict:
        """Process outgoing message queue (batched)."""
        total = len(self.store.message_queue)
        delivered = sum(1 for m in self.store.message_queue if m.delivered)
        
        return {
            "total": total,
            "delivered": delivered,
            "pending": total - delivered
        }
