import os
import json
import pandas as pd
import numpy as np

from src.config.schema import ExperimentConfig
from src.simulation.model import SangamVidyutModel
from src.simulation.agents.consumer import ConsumerAgent
from src.simulation.agents.adapters import create_consumer_from_household_record

OUT_DIR = 'outputs/validation/phase_4e_2'

def setup_synthetic_model(config: ExperimentConfig) -> SangamVidyutModel:
    model = SangamVidyutModel(config)
    
    seed = config.simulation.seed
    pop_path = f'data/processed/households/synthetic/population_500_seed_{seed}.parquet'
    if not os.path.exists(pop_path):
        pop_path = 'data/processed/households/synthetic/population_500_seed_42.parquet'
        
    pop_df = pd.read_parquet(pop_path).head(config.simulation.n_agents)
    
    # Remove default mock consumer agents
    for agent in list(model.agents):
        if isinstance(agent, ConsumerAgent):
            if hasattr(agent, 'pos') and agent.pos is not None:
                model.grid.remove_agent(agent)
            model.agents.remove(agent)
            
    # Inject synthetic agents
    for i, row in pop_df.iterrows():
        agent = create_consumer_from_household_record(model, row)
        model.grid.place_agent(agent, i)
        
    # Re-seed initial adopters on the synthetic agents
    initial_nodes = np.random.choice(model.G.nodes(), size=5, replace=False)
    for node in initial_nodes:
        agent_list = model.grid.get_cell_list_contents([node])
        for a in agent_list:
            if isinstance(a, ConsumerAgent):
                a.is_adopter = True
                a.sir_state = 1
        
    return model

def calculate_distribution(p_array):
    if len(p_array) == 0:
        return {}
    return {
        "min": float(np.min(p_array)),
        "max": float(np.max(p_array)),
        "mean": float(np.mean(p_array)),
        "median": float(np.median(p_array)),
        "std": float(np.std(p_array)),
        "p10": float(np.percentile(p_array, 10)),
        "p25": float(np.percentile(p_array, 25)),
        "p50": float(np.percentile(p_array, 50)),
        "p75": float(np.percentile(p_array, 75)),
        "p90": float(np.percentile(p_array, 90))
    }

def run_invariant_checks(model):
    s = sum(1 for a in model.agents if getattr(a, 'sir_state', -1) == 0)
    i = sum(1 for a in model.agents if getattr(a, 'sir_state', -1) == 1)
    r = sum(1 for a in model.agents if getattr(a, 'sir_state', -1) == 2)
    consumers = sum(1 for a in model.agents if isinstance(a, ConsumerAgent))
    assert s + i + r == consumers, f"SIR conservation failed: {s}+{i}+{r} != {consumers}"
    
    for a in model.agents:
        if isinstance(a, ConsumerAgent):
            assert 0.0 <= getattr(a, 'adoption_probability', 0.0) <= 1.0, "Probability bound failed"

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    results = {}
    
    print("1. Distribution Comparison")
    dist_results = {}
    for provider in ["legacy", "empirical"]:
        config = ExperimentConfig()
        config.simulation.baseline_provider = provider
        model = setup_synthetic_model(config)
        
        p_bases = []
        for a in model.agents:
            if isinstance(a, ConsumerAgent):
                if provider == "empirical":
                    p = model.baseline_provider.predict(a)
                else:
                    features = pd.DataFrame([[a.income, a.home_owner]])
                    p = model.baseline_model.predict_proba(features)[0]
                p_bases.append(p)
                
        dist_results[provider] = calculate_distribution(np.array(p_bases))
    
    results["distribution"] = dist_results
    with open(f"{OUT_DIR}/distribution.json", "w") as f:
        json.dump(dist_results, f, indent=2)
        
    print("2. Controlled Dynamics Test")
    dynamics_results = {}
    for provider in ["legacy", "empirical"]:
        config = ExperimentConfig()
        config.simulation.baseline_provider = provider
        config.simulation.timesteps = 12
        config.llm.enabled = False
        config.government.dynamic_subsidy = False
        
        model = setup_synthetic_model(config)
        
        history = []
        for step in range(13):
            if step > 0:
                model.step()
            run_invariant_checks(model)
            
            df = model.datacollector.get_model_vars_dataframe().iloc[-1]
            history.append({
                "timestep": int(df["timestep"]),
                "susceptible": int(df["susceptible_count"]),
                "infected": int(df["infected_count"]),
                "recovered": int(df["recovered_count"]),
                "new_adoptions": int(df["new_adoptions"]),
                "adoption_rate": float(df["adoption_rate"])
            })
        dynamics_results[provider] = history
    
    with open(f"{OUT_DIR}/controlled_dynamics.json", "w") as f:
        json.dump(dynamics_results, f, indent=2)
        
    print("3. Parameterized Diffusion Test")
    diffusion_results = []
    betas = {"low": 0.05, "intermediate": 0.15, "high": 0.30}
    topologies = ["watts_strogatz", "barabasi_albert"]
    
    for provider in ["legacy", "empirical"]:
        for top in topologies:
            for b_name, b_val in betas.items():
                config = ExperimentConfig()
                config.simulation.baseline_provider = provider
                config.network.topology = top
                config.sir.beta = b_val
                config.simulation.timesteps = 12
                config.llm.enabled = False
                
                model = setup_synthetic_model(config)
                for _ in range(12):
                    model.step()
                    
                run_invariant_checks(model)
                df = model.datacollector.get_model_vars_dataframe()
                
                final_rate = float(df["adoption_rate"].iloc[-1])
                peak_new = int(df["new_adoptions"].max())
                
                # Check tipping (e.g. >10% adoption)
                tipping_step = int(df[df["adoption_rate"] > 0.1]["timestep"].min()) if (df["adoption_rate"] > 0.1).any() else -1
                
                diffusion_results.append({
                    "provider": provider,
                    "topology": top,
                    "beta_level": b_name,
                    "final_adoption": final_rate,
                    "peak_new_adoptions": peak_new,
                    "tipping_quarter": tipping_step
                })
                
    pd.DataFrame(diffusion_results).to_csv(f"{OUT_DIR}/parameterized_diffusion.csv", index=False)
    
    print("4. Economic Condition Test")
    economic_results = []
    subsidy_levels = [0.0, 2000.0, 5000.0]
    
    for provider in ["legacy", "empirical"]:
        for sub in subsidy_levels:
            config = ExperimentConfig()
            config.simulation.baseline_provider = provider
            config.government.dynamic_subsidy = False
            config.government.base_subsidy = sub
            config.simulation.timesteps = 12
            config.llm.enabled = False
            
            model = setup_synthetic_model(config)
            for _ in range(12):
                model.step()
                
            run_invariant_checks(model)
            df = model.datacollector.get_model_vars_dataframe()
            economic_results.append({
                "provider": provider,
                "subsidy": sub,
                "final_adoption": float(df["adoption_rate"].iloc[-1])
            })
            
    pd.DataFrame(economic_results).to_csv(f"{OUT_DIR}/economic_condition.csv", index=False)
    
    print("5. Cognitive Condition Test")
    cognitive_results = []
    for provider in ["legacy", "empirical"]:
        config = ExperimentConfig()
        config.simulation.baseline_provider = provider
        config.llm.enabled = True
        config.llm.provider = "mock"
        config.simulation.timesteps = 4
        
        model = setup_synthetic_model(config)
        for _ in range(4):
            model.step()
            
        run_invariant_checks(model)
        df = model.datacollector.get_model_vars_dataframe().iloc[-1]
        
        # total step decisions vs llm decisions across 4 steps
        df_all = model.datacollector.get_model_vars_dataframe()
        total_rule = int(df_all["step_rule_decisions"].sum())
        total_llm = int(df_all["step_llm_decisions"].sum())
        
        cognitive_results.append({
            "provider": provider,
            "final_adoption": float(df["adoption_rate"]),
            "rule_decisions": total_rule,
            "llm_decisions": total_llm,
            "llm_calls": int(df["cumulative_llm_calls"])
        })
        
    with open(f"{OUT_DIR}/cognitive_condition.json", "w") as f:
        json.dump(cognitive_results, f, indent=2)
        
    print("6. Monte Carlo Stability Test")
    mc_results = []
    seeds = [42, 100, 200, 300, 400]
    for provider in ["legacy", "empirical"]:
        adoptions = []
        for s in seeds:
            config = ExperimentConfig()
            config.simulation.baseline_provider = provider
            config.simulation.seed = s
            config.simulation.timesteps = 12
            config.llm.enabled = False
            
            model = setup_synthetic_model(config)
            for _ in range(12):
                model.step()
                
            run_invariant_checks(model)
            adoptions.append(float(model.datacollector.get_model_vars_dataframe()["adoption_rate"].iloc[-1]))
            
        mc_results.append({
            "provider": provider,
            "mean_final_adoption": float(np.mean(adoptions)),
            "std_final_adoption": float(np.std(adoptions)),
            "min_final_adoption": float(np.min(adoptions)),
            "max_final_adoption": float(np.max(adoptions))
        })
        
    with open(f"{OUT_DIR}/monte_carlo_stability.json", "w") as f:
        json.dump(mc_results, f, indent=2)

    print("All validation runs completed successfully.")

if __name__ == '__main__':
    main()
