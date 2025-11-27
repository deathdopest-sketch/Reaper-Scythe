"""
Necronomicon Learning System

The Necronomicon is an interactive learning system for the Reaper language,
providing comprehensive courses, tutorials, challenges, and AI-powered assistance.

Features:
- Interactive tutorials and lessons
- Code playground with sandboxing
- Challenge validation system
- Progress tracking and badges
- Quiz system with certifications
- AI assistant integration (Hack Benjamin, Thanatos)
"""

__version__ = "0.1.0"
__author__ = "Reaper Security Team"

# Import core components
from .core import (
    Necronomicon,
    Lesson,
    Challenge,
    Quiz,
    Course,
    ProgressTracker,
    load_course,
    create_course,
)

__all__ = [
    'Necronomicon',
    'Lesson',
    'Challenge',
    'Quiz',
    'Course',
    'ProgressTracker',
    'load_course',
    'create_course',
]

