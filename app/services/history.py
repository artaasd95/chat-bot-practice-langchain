"""History service for managing conversation history in the chat graph."""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc
from loguru import logger
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage

from app.database.models import ChatSession, ChatMessage
from app.database.database import get_db


class HistoryService:
    """Service for managing conversation history."""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def load_conversation_history(
        self, 
        session_id: str, 
        limit: int = 10
    ) -> List[BaseMessage]:
        """Load conversation history for a session.
        
        Args:
            session_id: The chat session ID.
            limit: Maximum number of messages to load.
            
        Returns:
            List of BaseMessage objects representing the conversation history.
        """
        try:
            # Get the chat session
            session = self.db.query(ChatSession).filter(
                ChatSession.id == session_id
            ).first()
            
            if not session:
                logger.warning(f"Chat session {session_id} not found")
                return []
            
            # Get recent messages
            messages = self.db.query(ChatMessage).filter(
                ChatMessage.session_id == session_id
            ).order_by(desc(ChatMessage.created_at)).limit(limit).all()
            
            # Reverse to get chronological order
            messages.reverse()
            
            # Convert to LangChain messages
            langchain_messages = []
            for msg in messages:
                if msg.message_type == "human":
                    langchain_messages.append(HumanMessage(content=msg.content))
                elif msg.message_type == "ai":
                    langchain_messages.append(AIMessage(content=msg.content))
                elif msg.message_type == "system":
                    langchain_messages.append(SystemMessage(content=msg.content))
            
            logger.info(f"Loaded {len(langchain_messages)} messages for session {session_id}")
            return langchain_messages
            
        except Exception as e:
            logger.error(f"Error loading conversation history: {str(e)}")
            return []
    
    async def save_message(
        self, 
        session_id: str, 
        content: str, 
        message_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[ChatMessage]:
        """Save a message to the conversation history.
        
        Args:
            session_id: The chat session ID.
            content: The message content.
            message_type: Type of message ('human', 'ai', 'system').
            metadata: Optional metadata for the message.
            
        Returns:
            The saved ChatMessage object or None if failed.
        """
        try:
            # Ensure session exists
            session = self.db.query(ChatSession).filter(
                ChatSession.id == session_id
            ).first()
            
            if not session:
                logger.warning(f"Chat session {session_id} not found, creating new session")
                session = ChatSession(
                    id=session_id,
                    user_id=1,  # Default user ID, should be passed from context
                    title=f"Chat Session {session_id[:8]}"
                )
                self.db.add(session)
                self.db.commit()
            
            # Create new message
            message = ChatMessage(
                session_id=session_id,
                content=content,
                message_type=message_type,
                metadata=metadata or {}
            )
            
            self.db.add(message)
            self.db.commit()
            self.db.refresh(message)
            
            logger.info(f"Saved {message_type} message to session {session_id}")
            return message
            
        except Exception as e:
            logger.error(f"Error saving message: {str(e)}")
            self.db.rollback()
            return None
    
    async def save_human_message(self, session_id: str, content: str) -> Optional[ChatMessage]:
        """Save a human message."""
        return await self.save_message(session_id, content, "human")
    
    async def save_ai_message(
        self, 
        session_id: str, 
        content: str, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[ChatMessage]:
        """Save an AI message."""
        return await self.save_message(session_id, content, "ai", metadata)
    
    async def save_system_message(self, session_id: str, content: str) -> Optional[ChatMessage]:
        """Save a system message."""
        return await self.save_message(session_id, content, "system")
    
    async def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Get a summary of the chat session.
        
        Args:
            session_id: The chat session ID.
            
        Returns:
            Dictionary containing session summary information.
        """
        try:
            session = self.db.query(ChatSession).filter(
                ChatSession.id == session_id
            ).first()
            
            if not session:
                return {"error": "Session not found"}
            
            message_count = self.db.query(ChatMessage).filter(
                ChatMessage.session_id == session_id
            ).count()
            
            return {
                "session_id": session_id,
                "title": session.title,
                "created_at": session.created_at.isoformat() if session.created_at else None,
                "updated_at": session.updated_at.isoformat() if session.updated_at else None,
                "message_count": message_count
            }
            
        except Exception as e:
            logger.error(f"Error getting session summary: {str(e)}")
            return {"error": str(e)}


def get_history_service(db: Session = None) -> HistoryService:
    """Get a history service instance.
    
    Args:
        db: Database session. If None, will get from dependency.
        
    Returns:
        HistoryService instance.
    """
    if db is None:
        db = next(get_db())
    return HistoryService(db)


def format_history_for_llm(messages: List[BaseMessage]) -> str:
    """Format conversation history for LLM context.
    
    Args:
        messages: List of conversation messages.
        
    Returns:
        Formatted string representation of the conversation.
    """
    if not messages:
        return "No previous conversation history."
    
    formatted_lines = ["Previous conversation:"]
    
    for msg in messages:
        if isinstance(msg, HumanMessage):
            formatted_lines.append(f"Human: {msg.content}")
        elif isinstance(msg, AIMessage):
            formatted_lines.append(f"Assistant: {msg.content}")
        elif isinstance(msg, SystemMessage):
            formatted_lines.append(f"System: {msg.content}")
    
    return "\n".join(formatted_lines)