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
        from src.simulation.llm.workflow import NORMALIZATION_EVENTS
        initial_norm_count = len(NORMALIZATION_EVENTS)
        
        try:
            decision = self.provider.generate_decision(agent_context)
            
            # Augment any newly recorded normalization events with context metadata
            for i in range(initial_norm_count, len(NORMALIZATION_EVENTS)):
                NORMALIZATION_EVENTS[i].update({
                    "provider": agent_context.get("provider", "unknown"),
                    "model_identifier": agent_context.get("model_identifier", "unknown"),
                    "prompt_version": agent_context.get("prompt_version", "unknown"),
                    "seed": getattr(self.provider.config.simulation, 'seed', "unknown"),
                    "decision_succeeded": True,
                    "fallback_triggered": False
                })
            
            return decision
        except Exception as e:
            self.failures += 1
            
            # Augment any newly recorded normalization events with context metadata
            for i in range(initial_norm_count, len(NORMALIZATION_EVENTS)):
                NORMALIZATION_EVENTS[i].update({
                    "provider": agent_context.get("provider", "unknown"),
                    "model_identifier": agent_context.get("model_identifier", "unknown"),
                    "prompt_version": agent_context.get("prompt_version", "unknown"),
                    "seed": getattr(self.provider.config.simulation, 'seed', "unknown"),
                    "decision_succeeded": False,
                    "fallback_triggered": self.fallback_enabled
                })
                
            if self.fallback_enabled:
                self.fallbacks += 1
                # Deterministic fallback: Use mathematical score
                return agent_context.get("combined_score", 0.0) >= 0.5
            raise e
