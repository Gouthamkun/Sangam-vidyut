import pytest
from src.config.schema import ExperimentConfig
from src.simulation.llm.providers import LangGraphLLMProvider
from src.simulation.llm.interface import LLMInterface
from src.simulation.llm.workflow import HouseholdDecision

# Mock Runnable that simulates a structured output LLM response
class DummyStructuredRunnable:
    def __init__(self, decision="WAIT", confidence=0.8):
        self.decision = decision
        self.confidence = confidence

    def invoke(self, input_data):
        return HouseholdDecision(
            decision=self.decision,
            confidence=self.confidence,
            reasoning_summary="Mocked explanation for test"
        )

class DummyLLM:
    def __init__(self, decision="WAIT", fail=False):
        self.decision = decision
        self.fail = fail

    def with_structured_output(self, schema):
        if self.fail:
            class FailingRunnable:
                def invoke(self, input_data):
                    raise ValueError("Simulated LLM API Error")
            return FailingRunnable()
        return DummyStructuredRunnable(self.decision)

@pytest.fixture
def base_config():
    config = ExperimentConfig()
    config.llm.provider = "langgraph"
    config.llm.cache_enabled = True
    config.llm.fallback_enabled = True
    return config

def test_langgraph_provider_adopt(base_config):
    # Inject dummy LLM that always adopts
    provider = LangGraphLLMProvider(base_config, llm_instance=DummyLLM(decision="ADOPT"))
    interface = LLMInterface(provider=provider, fallback_enabled=True)
    
    context = {"agent_id": 1, "income": 50000, "sir_score": 0.5, "combined_score": 0.6}
    decision = interface.decide(context)
    
    assert decision is True
    assert interface.failures == 0
    assert provider.call_count == 1

def test_langgraph_provider_wait(base_config):
    provider = LangGraphLLMProvider(base_config, llm_instance=DummyLLM(decision="WAIT"))
    interface = LLMInterface(provider=provider, fallback_enabled=True)
    
    context = {"agent_id": 2, "income": 50000, "sir_score": 0.5, "combined_score": 0.6}
    decision = interface.decide(context)
    
    assert decision is False
    assert provider.call_count == 1

def test_llm_caching(base_config):
    provider = LangGraphLLMProvider(base_config, llm_instance=DummyLLM(decision="ADOPT"))
    
    context1 = {"agent_id": 1, "income": 50000, "sir_score": 0.5}
    context2 = {"agent_id": 2, "income": 50000, "sir_score": 0.5} # structurally identical
    context3 = {"agent_id": 3, "income": 60000, "sir_score": 0.5} # different
    
    provider.generate_decision(context1)
    assert provider.call_count == 1
    assert provider.cache_misses == 1
    assert provider.cache_hits == 0
    
    # Should hit cache
    provider.generate_decision(context2)
    assert provider.call_count == 1
    assert provider.cache_misses == 1
    assert provider.cache_hits == 1
    
    # Should miss cache
    provider.generate_decision(context3)
    assert provider.call_count == 2
    assert provider.cache_misses == 2
    assert provider.cache_hits == 1

def test_fallback_behavior(base_config):
    provider = LangGraphLLMProvider(base_config, llm_instance=DummyLLM(fail=True))
    interface = LLMInterface(provider=provider, fallback_enabled=True)
    
    context = {"agent_id": 1, "combined_score": 0.8} # fallback threshold is >= 0.5
    
    # Should not raise exception, but use fallback
    decision = interface.decide(context)
    
    assert decision is True
    assert interface.failures == 1
    assert interface.fallbacks == 1

def test_fallback_disabled(base_config):
    provider = LangGraphLLMProvider(base_config, llm_instance=DummyLLM(fail=True))
    interface = LLMInterface(provider=provider, fallback_enabled=False)
    
    context = {"agent_id": 1, "combined_score": 0.8}
    
    # Should raise exception
    with pytest.raises(Exception):
        interface.decide(context)
