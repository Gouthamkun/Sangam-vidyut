import pytest
import os
from src.simulation.llm.workflow import build_cognitive_workflow, HouseholdDecision
from src.config.schema import ExperimentConfig as SimConfig
from src.simulation.model import SangamVidyutModel
from pydantic import ValidationError

def test_missing_api_key_raises_error(monkeypatch):
    """Verify that MockLLM cannot silently replace real LLM if API key is missing."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("SANGAM_VIDYUT_DRY_RUN", raising=False)
    with pytest.raises(ValueError, match="API authentication required"):
        build_cognitive_workflow(model_name="gpt-4o-mini")
        
def test_dummy_model_works(monkeypatch):
    """Verify that explicit dummy model works."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("SANGAM_VIDYUT_DRY_RUN", "1")
    workflow = build_cognitive_workflow(model_name="gpt-4o-mini")
    
    state = {"context": {"income": 0.5, "home_owner": 1}, "prompt": "", "decision": None, "error": None}
    state = workflow.invoke(state)
    
    assert state["decision"].decision == "WAIT"
    assert state["error"] is None

def test_structured_output_validation():
    """Verify malformed output raises validation errors."""
    with pytest.raises(ValidationError):
        HouseholdDecision(decision="INVALID", confidence=0.5, reasoning_summary="test")
        
    decision = HouseholdDecision(decision="ADOPT", confidence=8, reasoning_summary="test")
    assert decision.confidence == 0.8

def test_provenance_logging():
    """Verify that the model captures LLM provider configuration correctly."""
    config = SimConfig()
    config.llm.provider = "mock"
    model = SangamVidyutModel(config)
    assert model.llm_interface.provider.__class__.__name__ == "MockLLMProvider"

