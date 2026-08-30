from typing import Dict, Any
from src.simulation.llm.providers import BaseLLMProvider

class LLMInterface:
    """
    The LLM Interface routes requests from the ConsumerAgent to the configured LLM Provider.
    Includes fallback logic and metrics tracking.
    """
    def __init__(self, provider: BaseLLMProvider, fallback_enabled: bool = True):
        self.provider = provider
        self.fallback_enabled = fallback_enabled
        self.failures = 0
        self.fallbacks = 0
        
    def decide(self, agent_context: Dict[str, Any]) -> bool:
        """
        Takes the ambiguous agent context and returns a boolean adoption decision.
        """
        try:
            return self.provider.generate_decision(agent_context)
        except Exception as e:
            self.failures += 1
            if self.fallback_enabled:
                self.fallbacks += 1
                # Deterministic fallback: Use mathematical score
                return agent_context.get("combined_score", 0.0) >= 0.5
            raise e
