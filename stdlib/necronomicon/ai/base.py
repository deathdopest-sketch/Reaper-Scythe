"""
Base AI Assistant Class

Provides the foundation for all AI assistants in Necronomicon.
All AI processing happens locally - no corporate API dependencies.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Message:
    """Represents a message in the conversation."""
    role: str  # "user", "assistant", "system"
    content: str
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class AIAssistant(ABC):
    """
    Base class for AI assistants.
    
    All assistants use LOCAL models only - no corporate APIs.
    Supports Ollama, llama.cpp, or other local model backends.
    """
    
    def __init__(self, name: str, model_name: str = "local", context_window: int = 4096):
        """
        Initialize AI assistant.
        
        Args:
            name: Assistant name
            model_name: Name of local model to use
            context_window: Maximum context window size
        """
        self.name = name
        self.model_name = model_name
        self.context_window = context_window
        self.conversation_history: List[Message] = []
        self.context: Dict[str, Any] = {}  # Additional context (current lesson, course, etc.)
        self.local_model_available = False
        self._check_local_model()
    
    def _check_local_model(self):
        """Check if local AI model is available."""
        # Try to import Ollama
        try:
            import ollama
            self.local_model_available = True
            self.backend = "ollama"
        except ImportError:
            # Try llama.cpp or other backends
            self.local_model_available = False
            self.backend = "fallback"
    
    def set_context(self, key: str, value: Any):
        """Set context information (current lesson, course, etc.)."""
        self.context[key] = value
    
    def get_context(self, key: str, default: Any = None) -> Any:
        """Get context information."""
        return self.context.get(key, default)
    
    def add_message(self, role: str, content: str):
        """Add message to conversation history."""
        message = Message(role=role, content=content)
        self.conversation_history.append(message)
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []
    
    def get_context_for_prompt(self) -> str:
        """
        Generate context string for prompt.
        Includes conversation history and current context.
        """
        context_parts = []
        
        # Add current context
        if self.context:
            context_parts.append("Current Context:")
            for key, value in self.context.items():
                context_parts.append(f"- {key}: {value}")
        
        # Add recent conversation history (within context window)
        if self.conversation_history:
            context_parts.append("\nConversation History:")
            # Limit to recent messages to stay within context window
            recent_messages = self.conversation_history[-10:]  # Last 10 messages
            for msg in recent_messages:
                context_parts.append(f"{msg.role}: {msg.content}")
        
        return "\n".join(context_parts)
    
    @abstractmethod
    def generate_response(self, user_input: str) -> str:
        """
        Generate response to user input.
        
        Args:
            user_input: User's question or statement
            
        Returns:
            Assistant's response
        """
        pass
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Get system prompt that defines the assistant's personality and role."""
        pass
    
    def query(self, user_input: str) -> str:
        """
        Main interface for querying the assistant.
        
        Args:
            user_input: User's question
            
        Returns:
            Assistant's response
        """
        # Add user message to history
        self.add_message("user", user_input)
        
        # Generate response
        response = self.generate_response(user_input)
        
        # Add assistant response to history
        self.add_message("assistant", response)
        
        return response


class FallbackAssistant(AIAssistant):
    """Fallback assistant that uses rule-based responses when AI models aren't available."""
    
    def __init__(self, name: str):
        super().__init__(name)
    
    def generate_response(self, user_input: str) -> str:
        """Generate basic rule-based response."""
        user_lower = user_input.lower()
        
        # Simple keyword matching for common questions
        if "syntax" in user_lower or "how to" in user_lower:
            return "I can help with Reaper syntax! Try asking about specific topics like 'variables', 'functions', or 'types'."
        
        if "error" in user_lower:
            return "If you're seeing an error, check:\n1. Syntax (matching braces, quotes)\n2. Type declarations\n3. Variable names are correct\n\nShare the error message for more specific help!"
        
        if "hello" in user_lower or "hi" in user_lower:
            return f"Hello! I'm {self.name}. I'm here to help you learn Reaper. Ask me questions about the language, syntax, or your code!"
        
        return f"I'm {self.name}, your AI tutor. To provide better assistance, a local AI model (like Ollama) would need to be installed. For now, I can answer basic questions. Try asking about:\n- Reaper syntax\n- Variables and types\n- Functions\n- Common errors"
    
    def get_system_prompt(self) -> str:
        return "You are a helpful programming tutor."

