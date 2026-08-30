from typing import TypedDict, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, END
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig

class HouseholdDecision(BaseModel):
    decision: Literal["ADOPT", "WAIT"] = Field(description="The final decision of the household.")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence in the decision.")
    reasoning_summary: str = Field(description="Concise explanation for the decision.")

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
        # Default to a mock or generic ChatOpenAI if credentials allow
        # For CI/CD tests, this will be passed a FakeListChatModel
        from langchain_openai import ChatOpenAI
        import os
        if "OPENAI_API_KEY" in os.environ:
            llm_instance = ChatOpenAI(model=model_name, temperature=0.1)
        else:
            # Safe mock fallback for CI if no instance passed and no keys
            class DummyLLM:
                def with_structured_output(self, schema):
                    class DummyRunnable:
                        def invoke(self, input_text):
                            return HouseholdDecision(decision="WAIT", confidence=0.5, reasoning_summary="Mock LLM")
                    return DummyRunnable()
            llm_instance = DummyLLM()
            
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
