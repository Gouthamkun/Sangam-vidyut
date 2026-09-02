import pandas as pd
import numpy as np
from typing import Dict, Any, Optional

from src.config.schema import ExperimentConfig as BaseAppConfig
from src.simulation.model import SangamVidyutModel
from src.simulation.agents.consumer import ConsumerAgent
from src.simulation.network.generators import generate_network
from src.models.diffusion.sir import PureSIRModel
from src.analysis.metrics import detect_tipping_point
from experiments.schemas import ExperimentConfig, ExperimentResult, MultiSeedExperimentConfig

def get_base_config(exp_config: ExperimentConfig, multi_config: Optional[MultiSeedExperimentConfig] = None) -> BaseAppConfig:
    config = BaseAppConfig()
    config.simulation.n_agents = exp_config.n_agents
    config.simulation.timesteps = exp_config.timesteps
    config.simulation.seed = exp_config.seed
    config.network.topology = exp_config.topology
    
    if multi_config:
        # Apply Sweeps
        params = multi_config.parameters
        if "topology" in params:
            config.network.topology = params["topology"]
            exp_config.topology = params["topology"]
        if "beta" in params:
            config.sir.beta = params["beta"]
        if "ws_p" in params:
            config.network.ws_p = params["ws_p"]
        if "ws_k" in params:
            config.network.ws_k = params["ws_k"]
        if "ba_m" in params:
            config.network.ba_m = params["ba_m"]
        if "subsidy" in params:
            config.government.base_subsidy = params["subsidy"]
        if "panel_price" in params:
            config.industry.base_price = params["panel_price"]
        if "target_adoption_rate" in params:
            config.government.target_adoption_rate = params["target_adoption_rate"]
        if "lower_threshold" in params:
            config.cognitive.lower_threshold = params["lower_threshold"]
        if "upper_threshold" in params:
            config.cognitive.upper_threshold = params["upper_threshold"]
            
        # Apply Ablations
        if multi_config.ablation.disable_sir:
            config.sir.beta = 0.0
        if multi_config.ablation.disable_network:
            config.sir.beta = 0.0 # Network influence is driven by beta
        if multi_config.ablation.disable_dynamic_subsidy:
            config.government.dynamic_subsidy = False
        if multi_config.ablation.disable_dynamic_pricing:
            config.industry.dynamic_pricing = False
        if multi_config.ablation.disable_llm:
            config.cognitive.lower_threshold = 0.5
            config.cognitive.upper_threshold = 0.5
            config.llm.provider = "mock"
            
    return config

def run_static_baseline(exp_config: ExperimentConfig, multi_config: Optional[MultiSeedExperimentConfig] = None) -> ExperimentResult:
    config = get_base_config(exp_config, multi_config)
    model = SangamVidyutModel(config)
    
    consumer_agents = [a for a in model.agents if isinstance(a, ConsumerAgent)]
    
    income_data = [a.income for a in consumer_agents]
    home_owner_data = [a.home_owner for a in consumer_agents]
    X = pd.DataFrame({'income': income_data, 'home_owner': home_owner_data})
    
    probs = model.baseline_model.predict_proba(X)
    adoptions = (probs >= 0.5).astype(int)
    final_count = int(adoptions.sum())
    
    cumulative = [final_count] * exp_config.timesteps
    
    return ExperimentResult(
        experiment_id=exp_config.experiment_id,
        model_type=exp_config.model_type,
        seed=exp_config.seed,
        population=exp_config.n_agents,
        timesteps=exp_config.timesteps,
        final_adoption=final_count,
        final_adoption_rate=final_count / exp_config.n_agents,
        cumulative_adoptions=cumulative,
        tipping_point=None,
        tipping_point_reached=False,
        peak_new_adoption_rate=0.0,
        time_to_25_percent=0 if final_count >= 0.25 * exp_config.n_agents else None,
        time_to_50_percent=0 if final_count >= 0.50 * exp_config.n_agents else None,
        total_llm_calls=0,
        total_cache_hits=0,
        total_llm_failures=0,
        cumulative_co2_displaced=None
    )

def run_sir_only(exp_config: ExperimentConfig, multi_config: Optional[MultiSeedExperimentConfig] = None) -> ExperimentResult:
    config = get_base_config(exp_config, multi_config)
    
    np.random.seed(config.simulation.seed)
    G = generate_network(n=config.simulation.n_agents, config=config.network, seed=config.simulation.seed)
    
    sir = PureSIRModel(
        graph=G,
        beta=config.sir.beta,
        recovery_quarters=config.sir.recovery_duration_quarters
    )
    
    initial_nodes = np.random.choice(G.nodes(), size=5, replace=False)
    sir.seed_infection(initial_nodes)
    
    cumulative = []
    for _ in range(exp_config.timesteps):
        sir.step()
        counts = sir.get_counts()
        cumulative.append(counts["I"] + counts["R"])
        
    final_count = cumulative[-1]
    tp = detect_tipping_point(pd.Series(cumulative), exp_config.n_agents)
    
    diffs = np.diff([5] + cumulative) # 5 is initial seed
    peak_new_adoption = int(np.max(diffs))
    peak_rate = peak_new_adoption / exp_config.n_agents
    
    t25, t50 = None, None
    for t, val in enumerate(cumulative):
        if t25 is None and val >= 0.25 * exp_config.n_agents:
            t25 = t
        if t50 is None and val >= 0.50 * exp_config.n_agents:
            t50 = t
    
    return ExperimentResult(
        experiment_id=exp_config.experiment_id,
        model_type=exp_config.model_type,
        seed=exp_config.seed,
        population=exp_config.n_agents,
        timesteps=exp_config.timesteps,
        final_adoption=final_count,
        final_adoption_rate=final_count / exp_config.n_agents,
        cumulative_adoptions=cumulative,
        tipping_point=tp,
        tipping_point_reached=(tp is not None),
        peak_new_adoption_rate=peak_rate,
        time_to_25_percent=t25,
        time_to_50_percent=t50,
        total_llm_calls=0,
        total_cache_hits=0,
        total_llm_failures=0,
        cumulative_co2_displaced=None
    )

def run_abm(exp_config: ExperimentConfig, multi_config: Optional[MultiSeedExperimentConfig] = None, cognitive: bool = False) -> ExperimentResult:
    config = get_base_config(exp_config, multi_config)
    
    if not cognitive or (multi_config and multi_config.ablation.disable_llm):
        config.cognitive.lower_threshold = 0.5
        config.cognitive.upper_threshold = 0.5
        config.llm.provider = "mock"
    else:
        config.llm.provider = "mock" if (multi_config and multi_config.ablation.force_mock_llm) else "langgraph"
        config.llm.cache_enabled = True
        
    model = SangamVidyutModel(config)
    
    for _ in range(exp_config.timesteps):
        model.step()
        
    df = model.datacollector.get_model_vars_dataframe()
    cumulative = df["adoption_count"].tolist()[1:] 
    cumulative = cumulative[:exp_config.timesteps]
    
    final_count = int(df["adoption_count"].iloc[-1])
    tp = detect_tipping_point(df["adoption_count"], exp_config.n_agents)
    
    diffs = np.diff([5] + cumulative)
    peak_new_adoption = int(np.max(diffs))
    peak_rate = peak_new_adoption / exp_config.n_agents
    
    t25, t50 = None, None
    for t, val in enumerate(cumulative):
        if t25 is None and val >= 0.25 * exp_config.n_agents:
            t25 = t
        if t50 is None and val >= 0.50 * exp_config.n_agents:
            t50 = t
    
    return ExperimentResult(
        experiment_id=exp_config.experiment_id,
        model_type=exp_config.model_type,
        seed=exp_config.seed,
        population=exp_config.n_agents,
        timesteps=exp_config.timesteps,
        final_adoption=final_count,
        final_adoption_rate=final_count / exp_config.n_agents,
        cumulative_adoptions=cumulative,
        tipping_point=tp,
        tipping_point_reached=(tp is not None),
        peak_new_adoption_rate=peak_rate,
        time_to_25_percent=t25,
        time_to_50_percent=t50,
        total_llm_calls=int(df["cumulative_llm_calls"].iloc[-1]),
        total_cache_hits=int(df["cumulative_cache_hits"].iloc[-1]),
        total_llm_failures=int(df["cumulative_llm_failures"].iloc[-1]),
        cumulative_co2_displaced=float(df["estimated_emissions_reduction"].iloc[-1])
    )

def run_experiment(exp_config: ExperimentConfig, multi_config: Optional[MultiSeedExperimentConfig] = None) -> ExperimentResult:
    if exp_config.model_type == "STATIC_BASELINE":
        return run_static_baseline(exp_config, multi_config)
    elif exp_config.model_type == "SIR_ONLY":
        return run_sir_only(exp_config, multi_config)
    elif exp_config.model_type == "DETERMINISTIC_ABM":
        return run_abm(exp_config, multi_config, cognitive=False)
    elif exp_config.model_type == "FULL_COGNITIVE_ABM":
        return run_abm(exp_config, multi_config, cognitive=True)
    else:
        raise ValueError(f"Unknown model_type: {exp_config.model_type}")
