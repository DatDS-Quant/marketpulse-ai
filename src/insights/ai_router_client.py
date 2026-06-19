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
        self.primary_model = os.getenv("AI_ROUTER_MODEL")
        
        fallback_models_str = os.getenv("AI_ROUTER_MODELS", "")
        self.fallback_models = [m.strip() for m in fallback_models_str.split(",")] if fallback_models_str else []
        
        self.timeout = float(os.getenv("AI_ROUTER_TIMEOUT_SECONDS", "30"))
        self.temperature = float(os.getenv("AI_ROUTER_TEMPERATURE", "0.2"))
        self.max_tokens = int(os.getenv("AI_ROUTER_MAX_TOKENS", "1200"))
        
        self.is_configured = bool(self.base_url and self.api_key and self.primary_model)
        self.last_attempted_model = None
        self.last_successful_model = None

    def _clean_json_content(self, content: str) -> str:
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        return content.strip()

    def generate_insights(self, prompt: str) -> Optional[Dict[str, Any]]:
        if not self.is_configured:
            logger.warning("AI Router is not fully configured.")
            return None

        # Build attempt list: Primary model + up to 2 fallbacks = max 3 models
        models_to_try = [self.primary_model]
        for fm in self.fallback_models:
            if fm and fm not in models_to_try:
                models_to_try.append(fm)
        models_to_try = models_to_try[:3]

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        with httpx.Client(timeout=self.timeout) as client:
            for attempt, model in enumerate(models_to_try, 1):
                self.last_attempted_model = model
                logger.info(f"AI Router attempt {attempt}/{len(models_to_try)} using model: {model}")
                
                data = {
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": self.temperature,
                    "max_tokens": self.max_tokens,
                    "response_format": {"type": "json_object"}
                }

                try:
                    response = client.post(self.base_url, headers=headers, json=data)
                    
                    # Explicit 429 handling: Stop trying to avoid key abuse
                    if response.status_code == 429:
                        logger.error("HTTP 429 Too Many Requests. Rate limit hit. Triggering immediate rule-based fallback.")
                        return None
                        
                    response.raise_for_status()
                    
                    resp_json = response.json()
                    content = resp_json.get("choices", [{}])[0].get("message", {}).get("content", "")
                    
                    cleaned_content = self._clean_json_content(content)
                    result = json.loads(cleaned_content)
                    
                    self.last_successful_model = model
                    return result
                    
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse JSON from model {model}: {e}")
                except httpx.HTTPStatusError as e:
                    logger.warning(f"HTTP Status error with model {model}: {e}")
                except httpx.RequestError as e:
                    logger.warning(f"Request error with model {model}: {e}")
                except Exception as e:
                    logger.warning(f"Unexpected error with model {model}: {e}")
                    
        logger.error("All AI Router attempts failed. Falling back to rule-based generator.")
        return None
