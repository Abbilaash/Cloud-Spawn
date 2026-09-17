from datetime import datetime, timezone
from typing import Dict, Any, List

def create_conversation_model(
    conversation_id: str
) -> Dict[str, Any]:
    now = datetime.now(timezone.utc).isoformat()
    return {
        "conversation_id": conversation_id,
        "messages": [],
        "created_at": now,
        "updated_at": now
    }

def create_message_model(
    role: str,
    content: str
) -> Dict[str, Any]:
    return {
        "role": role,
        "content": content,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
