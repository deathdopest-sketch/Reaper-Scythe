"""
Hack Benjamin AI Assistant

A beginner-friendly AI tutor for learning Reaper.
All processing happens locally - completely anonymous and free.
"""

from typing import Optional
from .base import AIAssistant, FallbackAssistant


class HackBenjamin(AIAssistant):
    """
    Hack Benjamin - Beginner-friendly AI tutor.
    
    Provides explanations, hints, and guidance for learning Reaper.
    Uses local AI models only - no corporate tracking.
    """
    
    def __init__(self, model_name: str = "llama3.2:1b"):
        """
        Initialize Hack Benjamin.
        
        Args:
            model_name: Name of local Ollama model to use (default: small fast model)
        """
        super().__init__("Hack Benjamin", model_name=model_name)
        
        # If no local model available, use fallback
        if not self.local_model_available:
            self.fallback = FallbackAssistant("Hack Benjamin")
    
    def get_system_prompt(self) -> str:
        """Get system prompt defining Benjamin's personality."""
        prompt = """You are Hack Benjamin, a friendly and patient programming tutor specializing in the Reaper security-focused programming language.

Your role:
- Help beginners learn Reaper syntax and concepts
- Explain programming concepts in simple, clear language
- Provide hints for challenges (not full solutions)
- Answer questions about Reaper language features
- Help debug code errors with helpful explanations

Personality:
- Patient and encouraging
- Uses simple explanations
- Provides examples when helpful
- Asks clarifying questions if needed

Guidelines:
- Never give full solutions to challenges - only hints
- Use Reaper-specific terminology (corpse for int, crypt for string, etc.)
- Provide code examples when explaining
- Be encouraging and supportive

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
            Benjamin's helpful response
        """
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
            
            # Query Ollama
            response = ollama.chat(
                model=self.model_name,
                messages=messages,
                options={
                    "temperature": 0.7,
                    "num_predict": 500,  # Limit response length
                }
            )
            
            return response["message"]["content"]
            
        except Exception as e:
            # If Ollama fails, fall back to basic response
            print(f"Ollama query failed: {e}")
            return self._generate_basic_response(user_input)
    
    def _generate_basic_response(self, user_input: str) -> str:
        """Generate basic helpful response."""
        user_lower = user_input.lower()
        
        # Reaper-specific help
        if "corpse" in user_lower or "integer" in user_lower:
            return """In Reaper, 'corpse' is the integer type. Here's how to use it:

```reaper
corpse age = 25;
corpse count = 0;
```

You can perform arithmetic: addition (+), subtraction (-), multiplication (*), division (/)."""
        
        if "crypt" in user_lower or "string" in user_lower:
            return """In Reaper, 'crypt' is the string type. Here's how to use it:

```reaper
crypt name = "Reaper";
crypt greeting = "Hello, " + name;
```

You can concatenate strings with +, and use harvest() to print them."""
        
        if "function" in user_lower:
            return """Functions in Reaper look like this:

```reaper
function add(corpse x, corpse y): corpse {
    return x + y;
}
```

- Start with 'function'
- List parameters with their types
- Specify return type after the colon
- Use 'return' to send a value back"""
        
        if "harvest" in user_lower:
            return """'harvest()' is Reaper's print function. It displays output:

```reaper
harvest("Hello, World!");
harvest(42);
harvest(x + y);
```

Use it to see the results of your code!"""
        
        if "challenge" in user_lower or "hint" in user_lower:
            return """I can give hints for challenges! Remember:
- Read the challenge description carefully
- Check the starter code for clues
- Try small steps first
- Test your code as you go

What specific part are you stuck on? I'll provide a helpful hint!"""
        
        # Generic response
        return """Hi! I'm Hack Benjamin, your Reaper tutor. I can help with:
- Syntax questions (variables, functions, types)
- Code debugging
- Challenge hints
- Learning Reaper concepts

Ask me anything about Reaper, and I'll explain it in beginner-friendly terms!

Note: For full AI capabilities, install Ollama (https://ollama.ai) and a model like 'llama3.2:1b'."""
    
    def provide_hint(self, challenge_description: str, user_code: Optional[str] = None) -> str:
        """
        Provide a hint for a challenge.
        
        Args:
            challenge_description: Description of the challenge
            user_code: User's current code (optional)
            
        Returns:
            Helpful hint (not the full solution)
        """
        if user_code:
            query = f"I'm working on this challenge: {challenge_description}\n\nMy code so far:\n{user_code}\n\nCan you give me a hint (not the full solution)?"
        else:
            query = f"I need a hint for this challenge: {challenge_description}\n\nCan you give me a helpful hint?"
        
        return self.query(query)
    
    def explain_concept(self, concept: str) -> str:
        """
        Explain a programming concept.
        
        Args:
            concept: Concept to explain (e.g., "functions", "variables", "loops")
            
        Returns:
            Clear explanation with examples
        """
        query = f"Explain {concept} in Reaper with a simple example"
        return self.query(query)
    
    def debug_code(self, code: str, error_message: Optional[str] = None) -> str:
        """
        Help debug code.
        
        Args:
            code: User's code that has an error
            error_message: Error message if available
            
        Returns:
            Helpful debugging guidance
        """
        if error_message:
            query = f"I have this error in my code:\n\n{error_message}\n\nHere's my code:\n{code}\n\nCan you help me fix it?"
        else:
            query = f"Can you help me debug this code?\n\n{code}"
        
        return self.query(query)

