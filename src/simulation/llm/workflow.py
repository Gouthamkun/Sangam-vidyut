from typing import TypedDict, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, END
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig

from pydantic import BaseModel, Field, field_validator

NORMALIZATION_EVENTS = []

class HouseholdDecision(BaseModel):
    decision: Literal["ADOPT", "WAIT"] = Field(description="The final decision of the household.")
    confidence: float = Field(description="Confidence in the decision (0.0 to 1.0).")
    reasoning_summary: str = Field(description="Concise explanation for the decision.")

    @field_validator('confidence', mode='before')
    def normalize_confidence(cls, v):
        raw_val = v
        reason = None
        normalized_val = None
        try:
            val = float(v)
            if val > 1.0:
                normalized_val = val / 10.0 if val <= 10.0 else val / 100.0
                reason = "integer confidence interpreted as percentage-scale artifact"
            else:
                normalized_val = val
        except (ValueError, TypeError):
            normalized_val = 0.5
            reason = "unrecoverable/invalid value replaced with default 0.5"

        if reason is not None:
            NORMALIZATION_EVENTS.append({
                "raw_value": raw_val,
                "normalized_value": normalized_val,
                "reason": reason
            })
            
        return normalized_val

class CognitiveState(TypedDict):
    context: Dict[str, Any]
    prompt: str
    decision: Optional[HouseholdDecision]
    error: Optional[str]

def build_cognitive_workflow(llm_instance=None, model_name: str = "gpt-4o-mini"):
    """
    Builds the LangGraph cognitive workflow.
    """
    if llm_instance is None:
        import os
        if model_name == "dummy" or os.environ.get("SANGAM_VIDYUT_DRY_RUN") == "1":
            class DummyLLM:
                def with_structured_output(self, schema):
                    class DummyRunnable:
                        def invoke(self, input_text):
                            return HouseholdDecision(decision="WAIT", confidence=0.5, reasoning_summary="Mock LLM")
                    return DummyRunnable()
            llm_instance = DummyLLM()
        elif model_name.startswith("llama") or "ollama" in model_name.lower():
            try:
                from langchain_ollama import ChatOllama
                base_llm = ChatOllama(model=model_name, temperature=0.1, format="json")
                class JSONOllamaRunnable:
                    def invoke(self, prompt):
                        full_prompt = prompt + "\nOutput strictly a single JSON object with exactly these keys: 'decision' (string, either 'ADOPT' or 'WAIT'), 'confidence' (float between 0.0 and 1.0), and 'reasoning_summary' (string)."
                        res = base_llm.invoke(full_prompt)
                        import json
                        try:
                            data = json.loads(res.content)
                            return HouseholdDecision(**data)
                        except Exception as e:
                            raise ValueError(f"JSON Parse Error: {e}, raw: {res.content}")
                structured_llm = JSONOllamaRunnable()
            except ImportError:
                raise ImportError("langchain_ollama is required for ChatOllama")
        elif "OPENAI_API_KEY" in os.environ:
            try:
                from langchain_openai import ChatOpenAI
                llm_instance = ChatOpenAI(model=model_name, temperature=0.1)
                structured_llm = llm_instance.with_structured_output(HouseholdDecision)
            except ImportError:
                raise ImportError("langchain_openai is required for ChatOpenAI")
        else:
            raise ValueError("API authentication required: OPENAI_API_KEY is not set.")
            
    if llm_instance is not None and not model_name.startswith("llama") and "ollama" not in model_name.lower() and model_name != "dummy":
        structured_llm = llm_instance.with_structured_output(HouseholdDecision)

    def prepare_context(state: CognitiveState):
        ctx = state["context"]
        prompt = (
            "You are a bounded-rationality household making a decision to ADOPT or WAIT on solar panels.\n"
            f"Income Level: {ctx.get('income')}\n"
            f"Home Owner: {bool(ctx.get('home_owner'))}\n"
            f"Panel Price: ${ctx.get('panel_price')}\n"
            f"Available Subsidy: ${ctx.get('subsidy')}\n"
            f"Affordability Score: {ctx.get('affordability')}\n"
            f"Adopting Neighbors: {ctx.get('adopting_neighbors')} out of {ctx.get('total_neighbors')}\n"
            f"Social Influence Score: {ctx.get('sir_score')}\n\n"
            "Constraints:\n"
            "- Do not invent numerical facts.\n"
            "- Do not change policy or simulation time.\n"
            "- Base your decision on affordability and social influence.\n"
        )
        return {"prompt": prompt}

    def reason_and_decide(state: CognitiveState):
        try:
            response = structured_llm.invoke(state["prompt"])
            return {"decision": response, "error": None}
        except Exception as e:
            return {"error": str(e)}

    workflow = StateGraph(CognitiveState)
    workflow.add_node("prepare", prepare_context)
    workflow.add_node("decide", reason_and_decide)
    workflow.set_entry_point("prepare")
    workflow.add_edge("prepare", "decide")
    workflow.add_edge("decide", END)

    return workflow.compile()
