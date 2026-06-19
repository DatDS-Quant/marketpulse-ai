import os
import json
import httpx
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class AIRouterClient:
    def __init__(self):
        self.base_url = os.getenv("AI_ROUTER_BASE_URL")
        self.api_key = os.getenv("AI_ROUTER_API_KEY")
        self.model = os.getenv("AI_ROUTER_MODEL")
        self.timeout = float(os.getenv("AI_ROUTER_TIMEOUT_SECONDS", "30"))
        self.temperature = float(os.getenv("AI_ROUTER_TEMPERATURE", "0.2"))
        self.max_tokens = int(os.getenv("AI_ROUTER_MAX_TOKENS", "1200"))
        
        self.is_configured = bool(self.base_url and self.api_key and self.model)

    def generate_insights(self, prompt: str) -> Optional[Dict[str, Any]]:
        if not self.is_configured:
            logger.warning("AI Router is not fully configured.")
            return None

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "response_format": {"type": "json_object"}
        }

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(self.base_url, headers=headers, json=data)
                response.raise_for_status()
                
                resp_json = response.json()
                content = resp_json.get("choices", [{}])[0].get("message", {}).get("content", "")
                
                # Clean markdown JSON tags if present
                content = content.strip()
                if content.startswith("```json"):
                    content = content[7:]
                if content.startswith("```"):
                    content = content[3:]
                if content.endswith("```"):
                    content = content[:-3]
                content = content.strip()

                return json.loads(content)
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from AI response: {e}")
            return None
        except httpx.HTTPError as e:
            logger.error(f"HTTP error calling AI Router: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error calling AI Router: {e}")
            return None
