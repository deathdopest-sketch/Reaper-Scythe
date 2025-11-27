"""
Necronomicon AI Assistants

Provides AI-powered assistance for learners:
- Hack Benjamin: Beginner-friendly tutor
- Thanatos: Advanced security expert (unlockable)
"""

__version__ = "0.1.0"

from .base import AIAssistant
from .benjamin import HackBenjamin
from .thanatos import Thanatos

__all__ = ['AIAssistant', 'HackBenjamin', 'Thanatos']
