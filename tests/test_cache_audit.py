import pytest
from src.config.schema import ExperimentConfig
from src.simulation.llm.providers import MockLLMProvider, LangGraphLLMProvider
from src.simulation.llm.interface import LLMInterface
from src.simulation.llm.workflow import HouseholdDecision, NORMALIZATION_EVENTS
from src.simulation.model import SangamVidyutModel

class TrackedDummyLLM:
    def __init__(self, decision="WAIT", confidence=0.8):
        self.decision = decision
        self.confidence = confidence
        self.invocations = 0

    def with_structured_output(self, schema):
        class DummyRunnable:
            def __init__(self, parent):
                self.parent = parent
            def invoke(self, input_data):
                self.parent.invocations += 1
                return HouseholdDecision(
                    decision=self.parent.decision,
                    confidence=self.parent.confidence,
                    reasoning_summary="Mocked"
                )
        return DummyRunnable(self)

@pytest.fixture
def base_config():
    config = ExperimentConfig()
    config.llm.provider = "langgraph"
    config.llm.cache_enabled = True
    return config

def test_within_seed_cache_reuse(base_config):
    """TEST 1: WITHIN-SEED CACHE REUSE"""
    llm = TrackedDummyLLM(decision="ADOPT")
    provider = LangGraphLLMProvider(base_config, llm_instance=llm)
    interface = LLMInterface(provider=provider, fallback_enabled=False)
    
    ctx = {"income": 50000, "sir_score": 0.5, "affordability": 0.6}
    
    res1 = interface.decide(ctx)
    res2 = interface.decide(ctx)
    
    assert res1 is True
    assert res2 is True
    assert provider.cache_misses == 1
    assert provider.cache_hits == 1
    assert llm.invocations == 1

def test_cross_seed_isolation(base_config):
    """TEST 2 & 5: CROSS-SEED ISOLATION AND CACHE LIFECYCLE"""
    llm_A = TrackedDummyLLM(decision="ADOPT")
    provider_A = LangGraphLLMProvider(base_config, llm_instance=llm_A)
    interface_A = LLMInterface(provider=provider_A, fallback_enabled=False)
    
    ctx = {"income": 50000, "sir_score": 0.5, "affordability": 0.6}
    
    res_A = interface_A.decide(ctx)
    assert res_A is True
    assert llm_A.invocations == 1
    
    # New seed/run starts, gets a new model instance and provider
    llm_B = TrackedDummyLLM(decision="WAIT")
    provider_B = LangGraphLLMProvider(base_config, llm_instance=llm_B)
    interface_B = LLMInterface(provider=provider_B, fallback_enabled=False)
    
    res_B = interface_B.decide(ctx)
    assert res_B is False
    assert llm_B.invocations == 1
    assert provider_B.cache_hits == 0

def test_cache_identity(base_config):
    """TEST 4: CACHE IDENTITY"""
    llm = TrackedDummyLLM(decision="ADOPT")
    provider = LangGraphLLMProvider(base_config, llm_instance=llm)
    interface = LLMInterface(provider=provider, fallback_enabled=False)
    
    ctx = {"income": 50000, "sir_score": 0.5, "prompt_version": "v1", "model_identifier": "mock", "provider": "LangGraphLLMProvider"}
    
    # 1. Base cache
    interface.decide(ctx)
    assert provider.cache_misses == 1
    
    # 2. Same context -> Hit
    interface.decide(ctx.copy())
    assert provider.cache_misses == 1
    
    # 3. Different prompt -> Miss
    ctx2 = ctx.copy()
    ctx2["prompt_version"] = "v2"
    interface.decide(ctx2)
    assert provider.cache_misses == 2
    
    # 4. Different model -> Miss
    ctx3 = ctx.copy()
    ctx3["model_identifier"] = "llama3.2:3b"
    interface.decide(ctx3)
    assert provider.cache_misses == 3
    
    # 5. Different provider -> Miss (Simulated by passing parameter into context hash)
    ctx4 = ctx.copy()
    ctx4["provider"] = "OtherProvider"
    interface.decide(ctx4)
    assert provider.cache_misses == 4
    
    # 6. Different model configuration -> Miss
    ctx5 = ctx.copy()
    ctx5["temperature"] = 0.9
    interface.decide(ctx5)
    assert provider.cache_misses == 5
    
    assert provider.cache_hits == 1
    assert llm.invocations == 5

def test_confidence_normalization():
    """TEST 6: CONFIDENCE NORMALIZATION"""
    NORMALIZATION_EVENTS.clear()
    
    # Valid float
    HouseholdDecision(decision="ADOPT", confidence=0.5, reasoning_summary="")
    assert len(NORMALIZATION_EVENTS) == 0
    
    # Integer-style artifact (e.g. 8)
    h = HouseholdDecision(decision="ADOPT", confidence=8, reasoning_summary="")
    assert h.confidence == 0.8
    assert len(NORMALIZATION_EVENTS) == 1
    assert NORMALIZATION_EVENTS[-1]["raw_value"] == 8
    assert NORMALIZATION_EVENTS[-1]["normalized_value"] == 0.8
    assert "integer confidence" in NORMALIZATION_EVENTS[-1]["reason"]
    
    # Integer-style artifact (e.g. 80)
    h = HouseholdDecision(decision="ADOPT", confidence=80, reasoning_summary="")
    assert h.confidence == 0.8
    assert len(NORMALIZATION_EVENTS) == 2
    
    # Unrecoverable string
    h = HouseholdDecision(decision="ADOPT", confidence="invalid", reasoning_summary="")
    assert h.confidence == 0.5
    assert len(NORMALIZATION_EVENTS) == 3
    assert NORMALIZATION_EVENTS[-1]["normalized_value"] == 0.5
    assert "unrecoverable" in NORMALIZATION_EVENTS[-1]["reason"]
