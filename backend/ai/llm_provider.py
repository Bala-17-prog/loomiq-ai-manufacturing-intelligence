import json
from typing import Dict, Any, Optional
from openai import OpenAI
from backend.config import settings

class LLMProvider:
    def __init__(self):
        self.api_key = settings.llm_api_key
        self.model = settings.llm_model or "gpt-3.5-turbo"
        self.base_url = settings.llm_base_url
        
        self.client = None
        if self.api_key:
            kwargs = {"api_key": self.api_key}
            if self.base_url:
                kwargs["base_url"] = self.base_url
            self.client = OpenAI(**kwargs)

    def is_available(self) -> bool:
        return self.client is not None

    def determine_intent(self, query: str, system_prompt: str) -> Optional[str]:
        """
        Uses the LLM to classify the intent of the user's query.
        """
        if not self.is_available():
            return None

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                temperature=0.0,
                max_tokens=50
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"[LLM Error - Intent] {e}")
            return None

    def generate_explanation(self, system_prompt: str, user_query: str, facts: Dict[str, Any]) -> Optional[str]:
        """
        Generates a natural language explanation strictly grounded in the provided facts.
        """
        if not self.is_available():
            return None

        facts_str = json.dumps(facts, indent=2)
        user_content = f"User Query: {user_query}\n\nFacts:\n{facts_str}"

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                temperature=0.0
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"[LLM Error - Explanation] {e}")
            return None
