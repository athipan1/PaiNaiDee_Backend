import os
import json
from typing import Dict, List, Optional
from openai import OpenAI


class TalkService:
    """Service for handling conversational AI interactions."""

    # Default role personalities
    DEFAULT_ROLES = {
        "A": {
            "name": "User",
            "personality": "You are a helpful and curious user asking questions about travel and tourism in Thailand.",
            "style": "casual, friendly, inquisitive"
        },
        "B": {
            "name": "Assistant",
            "personality": "You are a knowledgeable Thai tourism assistant. You provide helpful, accurate, and enthusiastic recommendations about Thai attractions, culture, and travel tips.",
            "style": "helpful, informative, polite, enthusiastic about Thailand"
        }
    }

    def __init__(self):
        # Initialize OpenAI client with configuration
        self.client = None
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.api_base = os.getenv('OPENAI_API_BASE', 'https://api.openai.com/v1')
        self.model = os.getenv('TALK_MODEL', 'gpt-3.5-turbo')
        self.max_tokens = int(os.getenv('TALK_MAX_TOKENS', '500'))
        self.temperature = float(os.getenv('TALK_TEMPERATURE', '0.7'))

        # Session storage (in production, this should be in a database or Redis)
        self.sessions = {}
        self.max_context_length = int(os.getenv('TALK_MAX_CONTEXT_LENGTH', '10'))

        if self.api_key:
            try:
                self.client = OpenAI(
                    api_key=self.api_key,
                    base_url=self.api_base
                )
            except Exception as e:
                print(f"Warning: Failed to initialize OpenAI client: {e}")

    def _get_role_prompt(self, role_name: str) -> str:
        """Get the system prompt for a specific role."""
        role_config = self.DEFAULT_ROLES.get(role_name, self.DEFAULT_ROLES["B"])
        return f"You are {role_config['name']}. {role_config['personality']} Your communication style is {role_config['style']}."

    def _get_session_context(self, session_id: str) -> List[Dict]:
        """Get conversation context for a session."""
        if not session_id:
            return []
        return self.sessions.get(session_id, [])

    def _update_session_context(self, session_id: str, user_message: str, assistant_reply: str, sender: str, receiver: str):
        """Update session context with new messages."""
        if not session_id:
            return

        if session_id not in self.sessions:
            self.sessions[session_id] = []

        # Add the conversation turn
        self.sessions[session_id].extend([
            {"role": "user", "content": f"[{sender}]: {user_message}"},
            {"role": "assistant", "content": f"[{receiver}]: {assistant_reply}"}
        ])

        # Trim context if it gets too long
        if len(self.sessions[session_id]) > self.max_context_length * 2:
            # Keep the most recent messages
            self.sessions[session_id] = self.sessions[session_id][-self.max_context_length * 2:]

    def _generate_fallback_response(self, sender: str, receiver: str, message: str) -> str:
        """Generate a fallback response when LLM is not available."""
        receiver_role = self.DEFAULT_ROLES.get(receiver, self.DEFAULT_ROLES["B"])

        # Simple rule-based responses for demonstration
        message_lower = message.lower()

        if any(word in message_lower for word in ['hello', 'hi', 'สวัสดี']):
            return f"สวัสดีครับ! ยินดีที่ได้พูดคุยกับคุณ How can I help you with information about Thailand?"

        elif any(word in message_lower for word in ['bangkok', 'กรุงเทพ']):
            return "Bangkok is an amazing city! There are so many attractions like the Grand Palace, Wat Pho, and Chatuchak Market. What specifically would you like to know about Bangkok?"

        elif any(word in message_lower for word in ['beach', 'ชายหาด', 'sea']):
            return "Thailand has some of the most beautiful beaches in the world! Popular destinations include Phuket, Koh Samui, Krabi, and Hua Hin. Are you looking for a specific type of beach experience?"

        elif any(word in message_lower for word in ['food', 'อาหาร', 'eat']):
            return "Thai cuisine is incredible! You must try Pad Thai, Tom Yum Goong, Green Curry, and Mango Sticky Rice. Are you looking for restaurant recommendations or curious about specific dishes?"

        else:
            return f"Thank you for your message! As a Thai tourism assistant, I'd be happy to help you learn more about Thailand's attractions, culture, and travel tips. Could you tell me more about what interests you?"

    def generate_response(self, sender: str, receiver: str, message: str, session_id: Optional[str] = None) -> Dict:
        """Generate a conversational response."""
        try:
            # If no OpenAI client is available, use fallback
            if not self.client:
                reply = self._generate_fallback_response(sender, receiver, message)
                if session_id:
                    self._update_session_context(session_id, message, reply, sender, receiver)
                return {"reply": reply, "session_id": session_id}

            # Build the conversation context
            messages = []

            # Add system prompt for the receiver's role
            system_prompt = self._get_role_prompt(receiver)
            messages.append({"role": "system", "content": system_prompt})

            # Add session context if available
            session_context = self._get_session_context(session_id)
            messages.extend(session_context)

            # Add the current message
            messages.append({"role": "user", "content": f"[{sender}]: {message}"})

            # Generate response using OpenAI
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                stop=[f"[{sender}]:"]  # Stop if the model tries to respond as the sender
            )

            reply = response.choices[0].message.content.strip()

            # Remove receiver prefix if the model added it
            if reply.startswith(f"[{receiver}]:"):
                reply = reply[len(f"[{receiver}]:"):].strip()

            # Update session context
            if session_id:
                self._update_session_context(session_id, message, reply, sender, receiver)

            return {"reply": reply, "session_id": session_id}

        except Exception as e:
            print(f"Error generating response: {e}")
            # Fallback to rule-based response
            reply = self._generate_fallback_response(sender, receiver, message)
            if session_id:
                self._update_session_context(session_id, message, reply, sender, receiver)
            return {"reply": reply, "session_id": session_id}

    def clear_session(self, session_id: str) -> bool:
        """Clear a conversation session."""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False

    def get_session_info(self, session_id: str) -> Dict:
        """Get information about a session."""
        if session_id not in self.sessions:
            return {"exists": False, "message_count": 0}

        return {
            "exists": True,
            "message_count": len(self.sessions[session_id]),
            "max_context": self.max_context_length * 2
        }
