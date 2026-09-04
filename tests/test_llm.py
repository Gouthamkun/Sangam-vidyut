import pytest
from src.config.schema import ExperimentConfig
from src.simulation.llm.providers import MockLLMProvider, LangGraphLLMProvider, BaseLLMProvider
from src.simulation.llm.interface import LLMInterface
from src.simulation.llm.workflow import HouseholdDecision
from src.simulation.model import SangamVidyutModel

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
    def __init__(self, decision="WAIT", confidence=0.8, fail=False, malformed=False):
        self.decision = decision
        self.confidence = confidence
        self.fail = fail
        self.malformed = malformed

    def with_structured_output(self, schema):
        if self.fail:
            class FailingRunnable:
                def invoke(self, input_data):
                    raise ValueError("Simulated LLM API Error")
            return FailingRunnable()
            
        if self.malformed:
            class MalformedRunnable:
                def invoke(self, input_data):
                    class BadDecision:
                        decision = "MAYBE"
                        confidence = 1.5
                    return BadDecision()
            return MalformedRunnable()
            
        return DummyStructuredRunnable(self.decision, self.confidence)

@pytest.fixture
def base_config():
    config = ExperimentConfig()
    config.llm.provider = "mock"  # Default to mock
    config.llm.cache_enabled = True
    config.llm.fallback_enabled = True
    return config

def test_langgraph_provider_adopt(base_config):
    base_config.llm.provider = "langgraph"
    provider = LangGraphLLMProvider(base_config, llm_instance=DummyLLM(decision="ADOPT"))
    interface = LLMInterface(provider=provider, fallback_enabled=True)
    
    context = {"agent_id": 1, "income": 50000, "sir_score": 0.5, "combined_score": 0.6}
    assert interface.decide(context) is True

def test_langgraph_provider_wait(base_config):
    base_config.llm.provider = "langgraph"
    provider = LangGraphLLMProvider(base_config, llm_instance=DummyLLM(decision="WAIT"))
    interface = LLMInterface(provider=provider, fallback_enabled=True)
    
    context = {"agent_id": 2, "income": 50000, "sir_score": 0.5, "combined_score": 0.6}
    assert interface.decide(context) is False

def test_adversarial_malformed_output(base_config):
    base_config.llm.provider = "langgraph"
    provider = LangGraphLLMProvider(base_config, llm_instance=DummyLLM(malformed=True))
    interface = LLMInterface(provider=provider, fallback_enabled=True)
    
    context = {"agent_id": 1, "combined_score": 0.6} 
    decision = interface.decide(context)
    
    assert decision is True
    assert interface.failures == 1
    assert interface.fallbacks == 1

def test_fallback_behavior(base_config):
    base_config.llm.provider = "langgraph"
    provider = LangGraphLLMProvider(base_config, llm_instance=DummyLLM(fail=True))
    interface = LLMInterface(provider=provider, fallback_enabled=True)
    
    context = {"agent_id": 1, "combined_score": 0.2}
    assert interface.decide(context) is False
    assert interface.failures == 1

def test_zero_width_threshold_routing(base_config):
    base_config.cognitive.lower_threshold = 0.5
    base_config.cognitive.upper_threshold = 0.5
    base_config.llm.provider = "mock"
    
    model = SangamVidyutModel(base_config)
    model.step()
    
    df = model.datacollector.get_model_vars_dataframe()
    assert df["step_llm_decisions"].sum() == 0

def test_cache_benchmark(base_config):
    base_config.simulation.n_agents = 500
    base_config.simulation.timesteps = 4
    base_config.cognitive.lower_threshold = 0.0 
    base_config.cognitive.upper_threshold = 1.0 
    base_config.llm.provider = "mock"
    
    model = SangamVidyutModel(base_config)
    for _ in range(4):
        model.step()
        
    df = model.datacollector.get_model_vars_dataframe()
    total_llm_decisions = df["step_llm_decisions"].sum()
    
    hits = model.llm_interface.provider.cache_hits
    misses = model.llm_interface.provider.cache_misses
    invocations = model.llm_interface.provider.call_count
    
    assert total_llm_decisions > 0
    assert hits > 100
    assert (hits + misses) == total_llm_decisions
