"""
Thanatos AI Assistant

An advanced AI security expert, unlockable after course completion.
All processing happens locally - completely anonymous and free.
"""

from typing import Optional
from .base import AIAssistant, FallbackAssistant


class Thanatos(AIAssistant):
    """
    Thanatos - Advanced security expert AI assistant.
    
    Unlockable after completing the basic course. Provides advanced
    security knowledge, penetration testing guidance, and expert-level
    assistance. Uses local AI models only - no corporate tracking.
    """
    
    def __init__(self, model_name: str = "llama3.2:3b"):
        """
        Initialize Thanatos.
        
        Args:
            model_name: Name of local Ollama model to use (default: larger model for better responses)
        """
        super().__init__("Thanatos", model_name=model_name)
        
        # Track unlock status
        self.unlocked = False
        self.unlock_requirement = "Complete 'basics_01_introduction' course"
        
        # If no local model available, use fallback
        if not self.local_model_available:
            self.fallback = FallbackAssistant("Thanatos")
    
    def check_unlock_status(self, progress_tracker) -> tuple[bool, str]:
        """
        Check if Thanatos should be unlocked.
        
        Args:
            progress_tracker: ProgressTracker instance to check course completion
            
        Returns:
            Tuple of (is_unlocked, reason_message)
        """
        # Check if basics course is completed
        basics_course_id = "basics_01_introduction"
        progress = progress_tracker.get_course_progress(basics_course_id)
        
        if progress >= 100.0:
            self.unlocked = True
            return True, "Course completed - Thanatos is now available!"
        else:
            return False, f"Complete {basics_course_id} course to unlock Thanatos ({progress:.0f}% complete)"
    
    def get_system_prompt(self) -> str:
        """Get system prompt defining Thanatos's personality and expertise."""
        prompt = """You are Thanatos, an advanced AI security expert specializing in penetration testing, security research, and ethical hacking.

Your role:
- Provide expert-level security guidance
- Explain advanced penetration testing concepts
- Help with security tool usage and techniques
- Discuss cryptographic principles
- Guide ethical hacking practices
- Explain vulnerability research and exploitation

Personality:
- Professional and knowledgeable
- Direct and technical
- Provides detailed explanations
- Assumes user has foundational knowledge
- Emphasizes ethical and legal practices

Guidelines:
- Always emphasize ethical hacking and legal compliance
- Provide technical depth in explanations
- Reference security frameworks and methodologies (OWASP, NIST, etc.)
- Explain both theory and practical application
- Warn about legal and ethical considerations

Important disclaimers:
- Only provide guidance for authorized security testing
- Emphasize the importance of proper authorization
- Discuss responsible disclosure practices
- Warn about legal consequences of unauthorized access

Current context: {context}
"""
        context_str = self.get_context_for_prompt()
        return prompt.format(context=context_str)
    
    def generate_response(self, user_input: str) -> str:
        """
        Generate response using local AI model or fallback.
        
        Args:
            user_input: User's question
            
        Returns:
            Thanatos's expert response
        """
        # Check if unlocked
        if not self.unlocked:
            return f"""Thanatos is locked. {self.unlock_requirement}.
            
Complete the basic course to unlock advanced security expertise."""
        
        # If local model not available, use fallback
        if not self.local_model_available:
            return self.fallback.query(user_input)
        
        # Try to use Ollama
        if self.backend == "ollama":
            return self._query_ollama(user_input)
        
        # Fallback to basic responses
        return self._generate_basic_response(user_input)
    
    def _query_ollama(self, user_input: str) -> str:
        """Query Ollama local model."""
        try:
            import ollama
            
            # Build messages for conversation
            messages = []
            
            # System prompt
            system_prompt = self.get_system_prompt()
            messages.append({
                "role": "system",
                "content": system_prompt
            })
            
            # Recent conversation history
            for msg in self.conversation_history[-5:]:  # Last 5 messages
                messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
            
            # Current user input
            messages.append({
                "role": "user",
                "content": user_input
            })
            
            # Query Ollama with advanced settings
            response = ollama.chat(
                model=self.model_name,
                messages=messages,
                options={
                    "temperature": 0.6,  # Lower for more focused responses
                    "num_predict": 800,  # Longer responses for detailed explanations
                    "top_p": 0.9,
                }
            )
            
            return response["message"]["content"]
            
        except Exception as e:
            # If Ollama fails, fall back to basic response
            print(f"Ollama query failed: {e}")
            return self._generate_basic_response(user_input)
    
    def _generate_basic_response(self, user_input: str) -> str:
        """Generate basic expert-level response."""
        user_lower = user_input.lower()
        
        # Security-specific help
        if "penetration" in user_lower or "pentest" in user_lower:
            return """Penetration testing follows structured methodologies:

1. **Reconnaissance**: Information gathering about target
2. **Scanning**: Network and service enumeration
3. **Enumeration**: Detailed system information gathering
4. **Vulnerability Analysis**: Identifying potential weaknesses
5. **Exploitation**: Attempting to exploit vulnerabilities (with authorization)
6. **Post-Exploitation**: Privilege escalation, persistence (if authorized)
7. **Reporting**: Documenting findings and recommendations

**Important**: Always ensure you have written authorization before testing. Unauthorized access is illegal.

Reaper's security libraries (phantom, crypt, wraith, specter) provide tools for authorized security testing."""
        
        if "cryptography" in user_lower or "crypto" in user_lower:
            return """Cryptography fundamentals in Reaper:

The `crypt` library provides cryptographic functions:
- Symmetric encryption (AES)
- Asymmetric encryption (RSA)
- Hashing (SHA-256, SHA-512)
- Digital signatures
- Key generation and management

**Security best practices**:
- Never hardcode keys or passwords
- Use strong, randomly generated keys
- Implement proper key management
- Use authenticated encryption when possible
- Understand the limitations of your chosen algorithms"""
        
        if "vulnerability" in user_lower or "exploit" in user_lower:
            return """Vulnerability research and exploitation require:

1. **Understanding**: Know the system/application architecture
2. **Identification**: Find potential vulnerabilities through testing
3. **Analysis**: Understand root cause and impact
4. **Exploitation**: Develop proof-of-concept (for authorized testing)
5. **Mitigation**: Recommend defensive measures

**Critical reminders**:
- Only test systems you own or have explicit permission to test
- Practice responsible disclosure for vulnerabilities found
- Follow coordinated disclosure timelines
- Document everything thoroughly

Reaper's security libraries support authorized vulnerability testing."""
        
        if "network" in user_lower or "packet" in user_lower:
            return """Network security and packet analysis in Reaper:

The `phantom` library provides network capabilities:
- Packet crafting and manipulation (via Scapy)
- Network scanning and enumeration
- Traffic analysis
- Protocol implementation

**Use cases**:
- Network reconnaissance (authorized)
- Traffic analysis
- Custom protocol testing
- Network security assessment

**Legal requirement**: Ensure you have authorization for any network testing."""
        
        # Generic expert response
        return f"""I'm Thanatos, your advanced security expert assistant. I can help with:
- Advanced penetration testing techniques
- Cryptographic principles and implementation
- Vulnerability research and exploitation
- Security tool development
- Network security and analysis
- Ethical hacking methodologies

**Important**: All activities must be conducted ethically and legally with proper authorization.

For full AI capabilities, install Ollama (https://ollama.ai) and a larger model like 'llama3.2:3b' for better expert-level responses.

What security topic would you like to explore?"""
    
    def unlock(self):
        """Manually unlock Thanatos (for testing or special cases)."""
        self.unlocked = True
    
    def explain_security_concept(self, concept: str) -> str:
        """
        Explain a security concept in depth.
        
        Args:
            concept: Security concept to explain
            
        Returns:
            Detailed expert explanation
        """
        query = f"Explain {concept} in depth, covering both theory and practical application for security professionals"
        return self.query(query)
    
    def provide_security_guidance(self, scenario: str) -> str:
        """
        Provide expert security guidance for a scenario.
        
        Args:
            scenario: Security scenario or question
            
        Returns:
            Expert guidance with best practices
        """
        query = f"Provide expert security guidance for this scenario: {scenario}. Include ethical and legal considerations."
        return self.query(query)

