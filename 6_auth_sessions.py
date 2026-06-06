"""
Authentication & Sessions — Login, tokens, multi-device sessions
Handles password validation, token generation, scope-based auth.
"""

import hashlib
import secrets
import time
from typing import Dict, Tuple, Optional
from dataclasses import dataclass


@dataclass
class User:
    id: str
    email: str
    password_hash: str
    created_at: float


@dataclass
class Session:
    session_id: str
    user_id: str
    device: str
    ip_address: str
    created_at: float
    last_active: float
    is_active: bool = True


@dataclass
class Token:
    token: str
    user_id: str
    scopes: list  # ["read", "write", "read_email", ...]
    created_at: float
    expires_at: float
    is_valid: bool = True


class AuthService:
    """Handles user authentication and session management."""

    def __init__(self):
        self.users: Dict[str, User] = {}  # user_id -> user
        self.sessions: Dict[str, Session] = {}  # session_id -> session
        self.tokens: Dict[str, Token] = {}  # token -> token_obj

    def register(self, email: str, password: str) -> User:
        """Register a new user."""
        if any(u.email == email for u in self.users.values()):
            raise ValueError("Email already registered")
        
        user_id = secrets.token_hex(8)
        password_hash = self._hash_password(password)
        user = User(
            id=user_id,
            email=email,
            password_hash=password_hash,
            created_at=time.time()
        )
        self.users[user_id] = user
        return user

    def login(self, email: str, password: str, device: str, ip: str) -> Tuple[User, Session, Token]:
        """Login user and create session + token."""
        # Find user by email
        user = None
        for u in self.users.values():
            if u.email == email:
                user = u
                break
        
        if not user:
            raise ValueError("User not found")
        
        # Verify password
        if not self._verify_password(password, user.password_hash):
            raise ValueError("Invalid password")
        
        # Create session
        session_id = secrets.token_hex(16)
        session = Session(
            session_id=session_id,
            user_id=user.id,
            device=device,
            ip_address=ip,
            created_at=time.time(),
            last_active=time.time()
        )
        self.sessions[session_id] = session
        
        # Create token
        token_str = secrets.token_urlsafe(32)
        token = Token(
            token=token_str,
            user_id=user.id,
            scopes=["read", "write", "read_email"],  # default scopes
            created_at=time.time(),
            expires_at=time.time() + (30 * 24 * 3600)  # 30 days
        )
        self.tokens[token_str] = token
        
        return user, session, token

    def validate_token(self, token_str: str) -> Optional[Token]:
        """Validate a token."""
        token = self.tokens.get(token_str)
        if token and token.is_valid and time.time() < token.expires_at:
            return token
        return None

    def logout(self, token_str: str):
        """Logout by invalidating token."""
        if token_str in self.tokens:
            self.tokens[token_str].is_valid = False

    def _hash_password(self, password: str) -> str:
        """Hash password using SHA256."""
        return hashlib.sha256(password.encode()).hexdigest()

    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash."""
        return self._hash_password(password) == password_hash
