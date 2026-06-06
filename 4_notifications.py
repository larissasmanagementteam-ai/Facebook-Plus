"""
Notification Fan-out — Push notifications and activity notifications
Uses fan-out-on-write for real-time delivery.
"""

import time
import uuid
from typing import Dict, List
from dataclasses import dataclass
from enum import Enum


class NotificationType(Enum):
    LIKE = "like"
    COMMENT = "comment"
    FRIEND_REQUEST = "friend_request"
    POST = "post"
    MESSAGE = "message"
    TAG = "tag"


@dataclass
class Notification:
    id: str
    user_id: str  # recipient
    type: NotificationType
    actor_id: str  # who triggered it
    actor_name: str
    subject_id: str  # post_id, etc.
    message: str
    timestamp: float
    read: bool = False
    
    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())[:8]


class NotificationStore:
    """Stores notifications in a user's inbox."""

    def __init__(self):
        self.notifications: Dict[str, List[Notification]] = {}  # user_id -> [notif]

    def add(self, notif: Notification):
        """Add a notification."""
        if notif.user_id not in self.notifications:
            self.notifications[notif.user_id] = []
        self.notifications[notif.user_id].append(notif)

    def get_notifications(self, user_id: str, limit: int = 50) -> List[Notification]:
        """Get recent notifications for a user."""
        return self.notifications.get(user_id, [])[-limit:]

    def unread_count(self, user_id: str) -> int:
        """Count unread notifications."""
        notifs = self.notifications.get(user_id, [])
        return sum(1 for n in notifs if not n.read)

    def mark_as_read(self, notif_id: str, user_id: str):
        """Mark a notification as read."""
        notifs = self.notifications.get(user_id, [])
        for n in notifs:
            if n.id == notif_id:
                n.read = True
                break


class FanOutService:
    """Fan-out notifications to followers (fan-out-on-write model)."""

    def __init__(self, store: NotificationStore):
        self.store = store

    def notify_like(self, liker_id: str, post_author_id: str, post_id: str, liker_name: str):
        """Notify user when someone likes their post."""
        notif = Notification(
            id="",
            user_id=post_author_id,
            type=NotificationType.LIKE,
            actor_id=liker_id,
            actor_name=liker_name,
            subject_id=post_id,
            message=f"{liker_name} liked your post",
            timestamp=time.time()
        )
        self.store.add(notif)

    def notify_comment(self, commenter_id: str, post_author_id: str, post_id: str, commenter_name: str, comment_text: str):
        """Notify user when someone comments on their post."""
        notif = Notification(
            id="",
            user_id=post_author_id,
            type=NotificationType.COMMENT,
            actor_id=commenter_id,
            actor_name=commenter_name,
            subject_id=post_id,
            message=f"{commenter_name} commented: {comment_text[:50]}...",
            timestamp=time.time()
        )
        self.store.add(notif)

    def notify_friend_request(self, requester_id: str, recipient_id: str, requester_name: str):
        """Notify user of incoming friend request."""
        notif = Notification(
            id="",
            user_id=recipient_id,
            type=NotificationType.FRIEND_REQUEST,
            actor_id=requester_id,
            actor_name=requester_name,
            subject_id=requester_id,
            message=f"{requester_name} sent you a friend request",
            timestamp=time.time()
        )
        self.store.add(notif)

    def fan_out_post(self, author_id: str, post_id: str, author_name: str, follower_ids: List[str], batch_size: int = 100):
        """Fan out post creation notification to followers (batched)."""
        for i in range(0, len(follower_ids), batch_size):
            batch = follower_ids[i:i+batch_size]
            for follower_id in batch:
                notif = Notification(
                    id="",
                    user_id=follower_id,
                    type=NotificationType.POST,
                    actor_id=author_id,
                    actor_name=author_name,
                    subject_id=post_id,
                    message=f"{author_name} posted something new",
                    timestamp=time.time()
                )
                self.store.add(notif)
