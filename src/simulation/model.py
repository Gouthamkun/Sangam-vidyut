import mesa
import numpy as np
from src.simulation.network.generators import generate_network
from src.simulation.agents.consumer import ConsumerAgent
from src.simulation.agents.government import GovernmentAgent
from src.simulation.agents.industry import IndustryAgent
from src.simulation.agents.environment import EnvironmentAgent
from src.simulation.agents.analysis import AnalysisAgent
from src.models.statistical.baseline import AdoptionLogisticRegression
from src.simulation.llm.providers import MockLLMProvider, LangGraphLLMProvider
from src.simulation.llm.interface import LLMInterface

class SangamVidyutModel(mesa.Model):
    """
    Agent-Based Model using Mesa 3.0+.
    Now includes a Cognitive Interface supporting real LangGraph routing.
    """
    def __init__(self, config):
        super().__init__()
        self.config = config
        
        # Override mesa's random with our deterministic seed
        self.random.seed(config.simulation.seed)
        np.random.seed(config.simulation.seed)
        
        # Authoritative global state
        self.timestep = 0
        self.new_adoptions = 0
        self.new_adoptions_last_step = 0
        
        # Per-step Metrics Tracking
        self.step_rule_decisions = 0
        self.step_llm_decisions = 0
        
        # Initialize LLM Interface
        if config.llm.provider == "langgraph":
            provider = LangGraphLLMProvider(config=config)
        else:
            provider = MockLLMProvider(config=config)
            
        self.llm_interface = LLMInterface(
            provider=provider, 
            fallback_enabled=config.llm.fallback_enabled
        )
        
        # Network Topology
        self.G = generate_network(n=config.simulation.n_agents, config=config.network, seed=config.simulation.seed)
        self.grid = mesa.space.NetworkGrid(self.G)
        
        # Baseline model initialization
        if config.simulation.baseline_provider == "empirical":
            from src.models.statistical.empirical_provider import EmpiricalBaselineProvider
            self.baseline_provider = EmpiricalBaselineProvider()
            self.baseline_model = None # Exclude legacy
        else:
            self.baseline_model = AdoptionLogisticRegression(random_state=config.simulation.seed)
            self.baseline_model.mock_fit(n_features=2)
            self.baseline_provider = None
        
        # Singleton Agents
        self.government = GovernmentAgent(self)
        self.industry = IndustryAgent(self)
        self.environment = EnvironmentAgent(self)
        self.analysis = AnalysisAgent(self)
        
        # Initialize Consumer Agents mapped to NetworkX nodes
        for node in self.G.nodes():
            income = np.random.rand()
            home_owner = np.random.choice([0, 1])
            agent = ConsumerAgent(model=self, income=income, home_owner=home_owner)
            self.grid.place_agent(agent, node)
            
        # Seed initial adopters
        initial_nodes = np.random.choice(self.G.nodes(), size=5, replace=False)
        for node in initial_nodes:
            agent_list = self.grid.get_cell_list_contents([node])
            for a in agent_list:
                if isinstance(a, ConsumerAgent):
                    a.is_adopter = True
                    a.sir_state = 1
            
        # Data Collection (Explicitly disambiguating per-step vs cumulative)
        self.datacollector = mesa.DataCollector(
            model_reporters={
                "timestep": "timestep",
                "adoption_count": "total_adopters",
                "adoption_rate": lambda m: m.total_adopters / m.config.simulation.n_agents,
                "susceptible_count": lambda m: sum(1 for a in m.agents if getattr(a, 'sir_state', -1) == 0),
                "infected_count": lambda m: sum(1 for a in m.agents if getattr(a, 'sir_state', -1) == 1),
                "recovered_count": lambda m: sum(1 for a in m.agents if getattr(a, 'sir_state', -1) == 2),
                "new_adoptions": "new_adoptions_last_step",
                "subsidy": lambda m: m.government.subsidy,
                "panel_price": lambda m: m.industry.panel_price,
                "estimated_emissions_reduction": lambda m: m.environment.co2_reduction,
                "step_rule_decisions": "step_rule_decisions",
                "step_llm_decisions": "step_llm_decisions",
                "cumulative_llm_calls": lambda m: m.llm_interface.provider.call_count,
                "cumulative_cache_hits": lambda m: m.llm_interface.provider.cache_hits,
                "cumulative_cache_misses": lambda m: m.llm_interface.provider.cache_misses,
                "cumulative_llm_failures": lambda m: m.llm_interface.failures,
                "cumulative_fallback_decisions": lambda m: m.llm_interface.fallbacks
            }
        )
        
        # Collect step 0
        self.datacollector.collect(self)

    @property
    def total_adopters(self) -> int:
        return sum(1 for a in self.agents if getattr(a, 'is_adopter', False))

    @property
    def current_subsidy(self) -> float:
        return self.government.subsidy

    @property
    def current_panel_price(self) -> float:
        return self.industry.panel_price

    def step(self):
        """Advance the model by one step."""
        self.new_adoptions_last_step = self.new_adoptions
        self.new_adoptions = 0
        
        # Reset per-step counters
        self.step_rule_decisions = 0
        self.step_llm_decisions = 0
        
        # 1. Government and Industry step (global economic variables)
        self.government.step()
        self.industry.step()
        
        # 2. Consumers step
        for agent in self.agents:
            if isinstance(agent, ConsumerAgent):
                agent.step()
        
        # 3. Environment and Analysis step (metrics)
        self.environment.step()
        self.analysis.step()
        
        self.datacollector.collect(self)
        self.timestep += 1
