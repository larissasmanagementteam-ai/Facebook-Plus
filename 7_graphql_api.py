"""
GraphQL API — Query/mutation execution, resolvers, scope-based authorization
Simulates GraphQL server for accessing Facebook data.
"""

import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class GraphQLUser:
    id: str
    name: str
    email: str
    followers: int
    posts: List[Dict]


class DataStore:
    """In-memory data store for GraphQL."""

    def __init__(self):
        self.users: Dict[str, GraphQLUser] = {}
        self.posts: Dict[str, Dict] = {}

    def seed(self):
        """Populate with sample data."""
        u1 = GraphQLUser(
            id="u1",
            name="Alice Johnson",
            email="alice@meta.com",
            followers=1250,
            posts=[
                {"id": "p1", "text": "Hello from Alice!", "likes": 45},
                {"id": "p2", "text": "Love this framework", "likes": 120},
            ]
        )
        u2 = GraphQLUser(
            id="u2",
            name="Bob Smith",
            email="bob@meta.com",
            followers=820,
            posts=[
                {"id": "p3", "text": "Big news coming soon!", "likes": 300},
            ]
        )
        self.users["u1"] = u1
        self.users["u2"] = u2

    def get_user(self, user_id: str) -> Optional[GraphQLUser]:
        """Retrieve a user."""
        return self.users.get(user_id)

    def create_post(self, user_id: str, text: str) -> Dict:
        """Create a new post."""
        post_id = f"p{int(time.time())}"
        post = {
            "id": post_id,
            "author_id": user_id,
            "text": text,
            "created_at": time.time(),
            "likes": 0
        }
        self.posts[post_id] = post
        
        # Add to user's posts
        if user_id in self.users:
            self.users[user_id].posts.append(post)
        
        return post


class GraphQLEngine:
    """Executes GraphQL queries and mutations."""

    def __init__(self, datastore: DataStore):
        self.datastore = datastore

    def execute(self, query: Dict, viewer_id: str, scopes: List[str]) -> Dict:
        """Execute a GraphQL query."""
        # Check authorization
        if "read" not in scopes:
            return {"errors": ["Missing read scope"]}
        
        # Handle different query types
        if "user" in query:
            return self._resolve_user_query(query["user"], viewer_id, scopes)
        
        return {"errors": ["Unknown query"]}

    def mutate(self, mutation: Dict, viewer_id: str, scopes: List[str]) -> Dict:
        """Execute a GraphQL mutation."""
        # Check authorization
        if "write" not in scopes:
            return {"errors": ["Missing write scope"]}
        
        # Handle different mutation types
        if "createPost" in mutation:
            return self._resolve_create_post(mutation["createPost"], viewer_id)
        
        return {"errors": ["Unknown mutation"]}

    def _resolve_user_query(self, user_query: Dict, viewer_id: str, scopes: List[str]) -> Dict:
        """Resolve a user query with scope-based field filtering."""
        user_id = user_query.get("id")
        fields = user_query.get("fields", [])
        
        user = self.datastore.get_user(user_id)
        if not user:
            return {"errors": ["User not found"]}
        
        # Scope-based field access
        response = {"id": user.id}
        
        if "name" in fields:
            response["name"] = user.name
        if "email" in fields and "read_email" in scopes:
            response["email"] = user.email
        if "followers" in fields:
            response["followers"] = user.followers
        if "posts" in fields:
            response["posts"] = user.posts
        
        return {"data": {"user": response}}

    def _resolve_create_post(self, create_post: Dict, user_id: str) -> Dict:
        """Resolve a createPost mutation."""
        text = create_post.get("text", "")
        post = self.datastore.create_post(user_id, text)
        return {"data": {"createPost": post}}
