import random
import hashlib
import json
from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers, with caching."""
    def __init__(self, config):
        self.config = config
        self.call_count = 0
        self.cache_hits = 0
        self.cache_misses = 0
        self._cache = {}

    def generate_decision(self, context: Dict[str, Any]) -> bool:
        if self.config.llm.cache_enabled:
            # Exclude non-structural elements like agent_id for caching
            cache_context = {k: v for k, v in context.items() if k not in ['agent_id']}
            key = hashlib.md5(json.dumps(cache_context, sort_keys=True).encode()).hexdigest()
            if key in self._cache:
                self.cache_hits += 1
                return self._cache[key]
                
        self.cache_misses += 1
        self.call_count += 1
        
        result = self._generate(context)
        
        if self.config.llm.cache_enabled:
            self._cache[key] = result
            
        return result

    @abstractmethod
    def _generate(self, context: Dict[str, Any]) -> bool:
        pass

class MockLLMProvider(BaseLLMProvider):
    """
    Mock LLM Provider for testing.
    Provides deterministic random decisions.
    """
    def __init__(self, config):
        super().__init__(config)
        self.rng = random.Random(config.simulation.seed)

    def _generate(self, context: Dict[str, Any]) -> bool:
        score = context.get("combined_score", 0.5)
        noise = self.rng.uniform(-0.15, 0.15)
        return (score + noise) >= 0.5

class LangGraphLLMProvider(BaseLLMProvider):
    """
    Real LangGraph-based LLM Provider.
    """
    def __init__(self, config, llm_instance=None):
        super().__init__(config)
        from src.simulation.llm.workflow import build_cognitive_workflow
        self.workflow = build_cognitive_workflow(llm_instance, config.llm.model)

    def _generate(self, context: Dict[str, Any]) -> bool:
        state = {"context": context, "prompt": "", "decision": None, "error": None}
        result = self.workflow.invoke(state)
        
        if result.get("error"):
            raise ValueError(f"LLM Reasoning failed: {result['error']}")
            
        decision = result.get("decision")
        if decision:
            return decision.decision == "ADOPT"
            
        raise ValueError("Invalid structured output from LangGraph")
