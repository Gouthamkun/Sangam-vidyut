import random
import hashlib
import json
from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers, with cognitive structural caching."""
    def __init__(self, config):
        self.config = config
        self.call_count = 0
        self.cache_hits = 0
        self.cache_misses = 0
        self._cache = {}

    def _generate_cache_key(self, context: Dict[str, Any]) -> str:
        """
        Creates a deterministic hash representing the decision-relevant structural context.
        Scientific Rationale for Modifications:
        1. income: Rounded to 1 decimal place (10 deciles). Bounded-rationality agents 
           do not distinguish between income differences < 10%.
        2. affordability: Rounded to 2 decimal places. Price elasticity bands.
        3. sir_score: Rounded to 4 decimal places to absorb negligible float drift.
        4. combined_score: Redundant derivative of the above; excluded to prevent fragmentation.
        5. timestep: Temporal reality only affects the decision via price, subsidy, and network state. 
           Absolute time does not alter human rationality rules. Removed.
        6. agent_id: Removed. Identity does not alter cognitive rules.
        """
        cache_context = {
            "income_decile": round(context.get("income", 0.0), 1),
            "home_owner": int(context.get("home_owner", 0)),
            "sir_score": round(context.get("sir_score", 0.0), 4),
            "affordability": round(context.get("affordability", 0.0), 2),
            "panel_price": round(context.get("panel_price", 0.0), 0),
            "subsidy": round(context.get("subsidy", 0.0), 0),
            "adopting_neighbors": int(context.get("adopting_neighbors", 0)),
            "total_neighbors": int(context.get("total_neighbors", 4)),
            "prompt_version": context.get("prompt_version", "v1"),
            "model_identifier": context.get("model_identifier", "mock"),
            "provider": context.get("provider", "unknown"),
            "temperature": context.get("temperature", 0.1)
        }
        
        return hashlib.md5(json.dumps(cache_context, sort_keys=True).encode()).hexdigest()

    def generate_decision(self, context: Dict[str, Any]) -> bool:
        key = self._generate_cache_key(context)
        
        if self.config.llm.cache_enabled and key in self._cache:
            self.cache_hits += 1
            return self._cache[key]
                
        self.cache_misses += 1
        self.call_count += 1
        
        if self.call_count % 10 == 0:
            print(f"LLM Call {self.call_count}, Misses: {self.cache_misses}, Hits: {self.cache_hits}", flush=True)
            
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
            if decision.decision not in ["ADOPT", "WAIT"]:
                raise ValueError(f"Invalid decision literal: {decision.decision}")
            return decision.decision == "ADOPT"
            
        raise ValueError("Invalid structured output from LangGraph")
