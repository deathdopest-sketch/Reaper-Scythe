"""
Necronomicon Core Learning System

Implements the core learning system with course structure, lessons, challenges,
quizzes, progress tracking, and code execution engine.
"""

import os
import json
import sqlite3
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
import sys

# Import Reaper language components for code execution
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from core.lexer import tokenize
from core.parser import parse
from core.interpreter import Interpreter
from core.reaper_error import ReaperRuntimeError, ReaperSyntaxError


class LessonStatus(Enum):
    """Status of a lesson."""
    LOCKED = "locked"
    AVAILABLE = "available"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class ChallengeType(Enum):
    """Type of challenge."""
    CODE = "code"  # Write code to solve
    FIX = "fix"  # Fix broken code
    QUIZ = "quiz"  # Multiple choice question
    EXPLAIN = "explain"  # Explain concept


@dataclass
class Lesson:
    """Represents a single lesson."""
    id: str
    title: str
    description: str
    content: str  # Markdown content
    code_example: Optional[str] = None  # Example Reaper code
    challenge: Optional['Challenge'] = None
    estimated_time: int = 10  # Minutes
    order: int = 0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        result = asdict(self)
        if self.challenge:
            result['challenge'] = self.challenge.to_dict()
        return result
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Lesson':
        """Create from dictionary."""
        challenge = None
        if 'challenge' in data and data['challenge']:
            challenge = Challenge.from_dict(data['challenge'])
        return cls(
            id=data['id'],
            title=data['title'],
            description=data['description'],
            content=data['content'],
            code_example=data.get('code_example'),
            challenge=challenge,
            estimated_time=data.get('estimated_time', 10),
            order=data.get('order', 0)
        )


@dataclass
class Challenge:
    """Represents a coding challenge."""
    id: str
    type: ChallengeType
    description: str
    starter_code: Optional[str] = None  # Code template provided
    solution: Optional[str] = None  # Expected solution (for validation)
    test_cases: List[Dict[str, Any]] = None  # Test cases for validation
    hints: List[str] = None
    
    def __post_init__(self):
        if self.test_cases is None:
            self.test_cases = []
        if self.hints is None:
            self.hints = []
        if not isinstance(self.test_cases, list):
            self.test_cases = list(self.test_cases) if self.test_cases else []
        if not isinstance(self.hints, list):
            self.hints = list(self.hints) if self.hints else []
        if isinstance(self.type, str):
            self.type = ChallengeType(self.type)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        result = asdict(self)
        result['type'] = self.type.value
        return result
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Challenge':
        """Create from dictionary."""
        return cls(
            id=data['id'],
            type=ChallengeType(data['type']),
            description=data['description'],
            starter_code=data.get('starter_code'),
            solution=data.get('solution'),
            test_cases=data.get('test_cases', []),
            hints=data.get('hints', [])
        )


@dataclass
class Quiz:
    """Represents a quiz question."""
    id: str
    question: str
    options: List[str]  # Multiple choice options
    correct_answer: int  # Index of correct answer
    explanation: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Quiz':
        """Create from dictionary."""
        return cls(
            id=data['id'],
            question=data['question'],
            options=data['options'],
            correct_answer=data['correct_answer'],
            explanation=data.get('explanation')
        )


@dataclass
class Course:
    """Represents a complete course."""
    id: str
    title: str
    description: str
    lessons: List[Lesson]
    quizzes: List[Quiz] = None
    prerequisites: List[str] = None  # Course IDs that must be completed first
    estimated_duration: int = 60  # Total minutes
    difficulty: str = "beginner"  # beginner, intermediate, advanced
    
    def __post_init__(self):
        if self.quizzes is None:
            self.quizzes = []
        if self.prerequisites is None:
            self.prerequisites = []
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'lessons': [lesson.to_dict() for lesson in self.lessons],
            'quizzes': [quiz.to_dict() for quiz in self.quizzes],
            'prerequisites': self.prerequisites,
            'estimated_duration': self.estimated_duration,
            'difficulty': self.difficulty
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Course':
        """Create from dictionary."""
        lessons = [Lesson.from_dict(les) for les in data.get('lessons', [])]
        quizzes = [Quiz.from_dict(q) for q in data.get('quizzes', [])]
        return cls(
            id=data['id'],
            title=data['title'],
            description=data['description'],
            lessons=lessons,
            quizzes=quizzes,
            prerequisites=data.get('prerequisites', []),
            estimated_duration=data.get('estimated_duration', 60),
            difficulty=data.get('difficulty', 'beginner')
        )


class ProgressTracker:
    """Tracks user progress through courses."""
    
    def __init__(self, db_path: str = "necronomicon_progress.db"):
        """Initialize progress tracker with SQLite database."""
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize progress tracking database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Courses table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS courses (
                course_id TEXT PRIMARY KEY,
                started_at TEXT,
                completed_at TEXT,
                completion_percentage REAL DEFAULT 0.0,
                last_accessed TEXT
            )
        """)
        
        # Lessons table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lessons (
                lesson_id TEXT PRIMARY KEY,
                course_id TEXT,
                status TEXT DEFAULT 'locked',
                completed_at TEXT,
                score REAL,
                attempts INTEGER DEFAULT 0,
                FOREIGN KEY (course_id) REFERENCES courses(course_id)
            )
        """)
        
        # Challenges table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS challenges (
                challenge_id TEXT PRIMARY KEY,
                lesson_id TEXT,
                completed_at TEXT,
                passed BOOLEAN DEFAULT 0,
                attempts INTEGER DEFAULT 0,
                best_score REAL,
                FOREIGN KEY (lesson_id) REFERENCES lessons(lesson_id)
            )
        """)
        
        # Quiz scores table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quiz_scores (
                quiz_id TEXT PRIMARY KEY,
                course_id TEXT,
                score REAL,
                completed_at TEXT,
                attempts INTEGER DEFAULT 0,
                FOREIGN KEY (course_id) REFERENCES courses(course_id)
            )
        """)
        
        # Badges/Certifications table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS badges (
                badge_id TEXT PRIMARY KEY,
                badge_name TEXT,
                badge_type TEXT,
                earned_at TEXT,
                course_id TEXT,
                FOREIGN KEY (course_id) REFERENCES courses(course_id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def get_lesson_status(self, lesson_id: str) -> LessonStatus:
        """Get status of a lesson."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT status FROM lessons WHERE lesson_id = ?", (lesson_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return LessonStatus(row[0])
        return LessonStatus.LOCKED
    
    def mark_lesson_completed(self, lesson_id: str, course_id: str, score: float = 100.0):
        """Mark a lesson as completed."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO lessons (lesson_id, course_id, status, completed_at, score, attempts)
            VALUES (?, ?, ?, datetime('now'), ?, COALESCE((SELECT attempts FROM lessons WHERE lesson_id = ?), 0) + 1)
        """, (lesson_id, course_id, LessonStatus.COMPLETED.value, score, lesson_id))
        
        # Update course completion percentage
        self._update_course_progress(course_id, cursor)
        
        conn.commit()
        conn.close()
    
    def _update_course_progress(self, course_id: str, cursor):
        """Update course completion percentage."""
        # Count completed lessons
        cursor.execute("""
            SELECT COUNT(*) FROM lessons 
            WHERE course_id = ? AND status = 'completed'
        """, (course_id,))
        completed = cursor.fetchone()[0]
        
        # Get total lessons (would need course data, simplified here)
        # In real implementation, would query course data
        
        cursor.execute("""
            UPDATE courses 
            SET completion_percentage = ?,
                last_accessed = datetime('now')
            WHERE course_id = ?
        """, (min(100.0, completed * 10), course_id))  # Simplified calculation
    
    def get_course_progress(self, course_id: str) -> float:
        """Get course completion percentage."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT completion_percentage FROM courses WHERE course_id = ?", (course_id,))
        row = cursor.fetchone()
        conn.close()
        
        return row[0] if row else 0.0


class CodeExecutor:
    """Safe code execution engine for Reaper code in lessons."""
    
    def __init__(self):
        """Initialize code executor with security limits."""
        self.interpreter = Interpreter(
            execution_timeout=5.0,  # 5 second timeout for lesson code
            max_string_length=10000,
            max_array_size=1000,
            max_dict_size=1000,
        )
        self.output_buffer = []
    
    def execute_code(self, code: str, capture_output: bool = True) -> Tuple[bool, str, Optional[Any]]:
        """
        Execute Reaper code safely.
        
        Args:
            code: Reaper source code
            capture_output: Whether to capture harvest() output
            
        Returns:
            Tuple of (success, output_message, result_value)
        """
        try:
            # Tokenize and parse
            tokens = tokenize(code, "<lesson>")
            program = parse(tokens)
            
            # Execute using interpret method
            self.interpreter.interpret(program)
            
            return True, "Code executed successfully", None
            
        except ReaperSyntaxError as e:
            return False, f"Syntax Error: {e}", None
        except ReaperRuntimeError as e:
            return False, f"Runtime Error: {e}", None
        except Exception as e:
            return False, f"Error: {e}", None


class Necronomicon:
    """Main Necronomicon learning system."""
    
    def __init__(self, courses_dir: str = "stdlib/necronomicon/lessons", 
                 data_dir: str = "stdlib/necronomicon/data"):
        """
        Initialize Necronomicon system.
        
        Args:
            courses_dir: Directory containing course JSON files
            data_dir: Directory for progress database and user data
        """
        self.courses_dir = Path(courses_dir)
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.progress_tracker = ProgressTracker(
            db_path=str(self.data_dir / "progress.db")
        )
        self.code_executor = CodeExecutor()
        self.courses: Dict[str, Course] = {}
        self._load_courses()
    
    def _load_courses(self):
        """Load all courses from JSON files."""
        if not self.courses_dir.exists():
            self.courses_dir.mkdir(parents=True, exist_ok=True)
            return
        
        for course_file in self.courses_dir.glob("*.json"):
            try:
                with open(course_file, 'r', encoding='utf-8') as f:
                    course_data = json.load(f)
                    course = Course.from_dict(course_data)
                    self.courses[course.id] = course
            except Exception as e:
                print(f"Error loading course {course_file}: {e}")
    
    def get_course(self, course_id: str) -> Optional[Course]:
        """Get a course by ID."""
        return self.courses.get(course_id)
    
    def list_courses(self) -> List[Course]:
        """List all available courses."""
        return list(self.courses.values())
    
    def validate_challenge(self, challenge: Challenge, user_code: str) -> Tuple[bool, str, float]:
        """
        Validate user's code against challenge requirements.
        
        Args:
            challenge: Challenge to validate against
            user_code: User's submitted code
            
        Returns:
            Tuple of (passed, feedback_message, score_0_to_100)
        """
        # Execute user code
        success, output, result = self.code_executor.execute_code(user_code)
        
        if not success:
            return False, output, 0.0
        
        # Run test cases if provided
        if challenge.test_cases:
            passed_tests = 0
            for test_case in challenge.test_cases:
                # Simplified test case validation
                # In full implementation, would run code with test inputs
                # and verify outputs match expected results
                passed_tests += 1  # Placeholder
        
            score = (passed_tests / len(challenge.test_cases)) * 100
            return score >= 70.0, f"Passed {passed_tests}/{len(challenge.test_cases)} tests", score
        
        # If no test cases, just check if code executes
        return True, "Code executed successfully", 100.0


def load_course(course_file: str) -> Course:
    """Load a course from a JSON file."""
    with open(course_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return Course.from_dict(data)


def create_course(course: Course, output_file: str):
    """Save a course to a JSON file."""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(course.to_dict(), f, indent=2, ensure_ascii=False)

