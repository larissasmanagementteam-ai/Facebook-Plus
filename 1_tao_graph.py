"""
TAO Social Graph — Distributed Storage for Social Network
Handles: nodes (users, posts, events), edges (friendships, likes, follows)
"""

import uuid
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class Node:
    id: str
    type: str  # "user", "post", "event", etc.
    data: Dict


@dataclass
class Edge:
    from_id: str
    to_id: str
    edge_type: str  # "friend", "liked", "posted", "follows"
    metadata: Dict = None


class TAOStore:
    """Simulates Facebook's TAO distributed cache."""

    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.edges: Dict[str, List[Edge]] = {}  # key: "from_id:edge_type"

    def create_node(self, node_type: str, data: Dict) -> Node:
        """Create a new node (user, post, event, etc.)."""
        node_id = str(uuid.uuid4())[:8]
        node = Node(id=node_id, type=node_type, data=data)
        self.nodes[node_id] = node
        return node

    def get_node(self, node_id: str) -> Optional[Node]:
        """Retrieve a node by ID."""
        return self.nodes.get(node_id)

    def create_edge(self, from_id: str, to_id: str, edge_type: str, metadata: Dict = None) -> Edge:
        """Create an edge between two nodes."""
        edge = Edge(from_id=from_id, to_id=to_id, edge_type=edge_type, metadata=metadata or {})
        key = f"{from_id}:{edge_type}"
        if key not in self.edges:
            self.edges[key] = []
        self.edges[key].append(edge)
        return edge

    def get_edges(self, from_id: str, edge_type: str) -> List[Edge]:
        """Get all edges of a given type from a node."""
        key = f"{from_id}:{edge_type}"
        return self.edges.get(key, [])

    def edge_exists(self, from_id: str, to_id: str, edge_type: str) -> bool:
        """Check if an edge exists."""
        edges = self.get_edges(from_id, edge_type)
        return any(e.to_id == to_id for e in edges)

    def delete_edge(self, from_id: str, to_id: str, edge_type: str) -> bool:
        """Delete an edge."""
        key = f"{from_id}:{edge_type}"
        if key in self.edges:
            self.edges[key] = [e for e in self.edges[key] if e.to_id != to_id]
            return True
        return False
