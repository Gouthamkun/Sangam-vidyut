import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import glob
import json
from src.simulation.live_runner import LiveSimulationRunner

st.set_page_config(page_title='Sangam Vidyut Dashboard', layout='wide')

@st.cache_data
def load_phase1_data():
    rows = []
    for f in glob.glob("outputs/experiments/phase_4f_1_rerun/raw/*_summary.json"):
        with open(f, "r") as file:
            d = json.load(file)
            rows.append({
                "subsidy": d["subsidy"],
                "topology": str(d["topology"]),
                "beta": str(d["beta"]),
                "p_base_mode": d["p_base_mode"],
                "final_adoption": d["final_adoption"],
                "model_class": d["model_class"]
            })
    return pd.DataFrame(rows)

@st.cache_data
def load_phase2_data():
    path = "outputs/experiments/phase_4f_2/tables/aggregated_factor_summary.csv"
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame()

@st.cache_data
def load_phase3_data():
    path = "outputs/experiments/phase_4f_3/tables/fixed_vs_dynamic.csv"
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame()

@st.cache_data
def load_trajectory(subsidy, topology, is_dynamic):
    dyn_str = "True" if is_dynamic else "False"
    path = f"outputs/experiments/phase_4f_3/raw/R3_DET_{subsidy}_{dyn_str}_{topology}_42_trajectory.csv"
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame()


# Load primary datasets
df1 = load_phase1_data()
df2 = load_phase2_data()
df3 = load_phase3_data()

def render_locked_research_results():
    # ==========================================
    # SIDEBAR
    # ==========================================
    st.title("Sangam Vidyut")
    st.markdown("**MODEL SIMULATION**")
    st.markdown("*This dashboard visualizes results from a bounded computational experiment. It is not a validated national forecast.*")
    
    st.header("Controls")
    phase = st.radio("Research Phase", ["Phase 4F.1", "Phase 4F.2", "Phase 4F.3"])
    
    # Dynamic UI Constraints based on Phase
    if phase == "Phase 4F.1":
        st.info("Phase 4F.1 focused on baseline bounds and affordability constraints.")
        subsidy = st.selectbox("Subsidy Level", [0.0, 1000.0, 5000.0], index=0)
        topology = st.selectbox("Topology", ["watts_strogatz", "barabasi_albert"])
        beta = st.selectbox("Beta (Transmission)", ["0.05", "0.15", "0.3"])
        p_base_mode = st.selectbox("Household Representation", ["empirical", "constant"])
        policy = "Fixed" # Not applicable
    elif phase == "Phase 4F.2":
        st.info("Phase 4F.2 focused on conditional mechanism activation.")
        subsidy = st.selectbox("Subsidy Level", [0.0, 1000.0, 2000.0, 3000.0, 4000.0, 5000.0], index=3)
        topology = st.selectbox("Topology", ["watts_strogatz", "barabasi_albert"])
        # Note: Beta loaded from csv are floats, so keep them as floats for 4F.2
        beta = st.selectbox("Beta (Transmission)", [0.05, 0.15, 0.3])
        p_base_mode = st.selectbox("Household Representation", ["empirical", "constant"])
        policy = "Fixed" # Not applicable
    elif phase == "Phase 4F.3":
        st.info("Phase 4F.3 held Beta and Household Representation constant to isolate policy robustness.")
        subsidy = st.selectbox("Subsidy Level", [1000.0, 2000.0, 3000.0, 4000.0, 5000.0], index=2)
        topology = st.selectbox("Topology", ["watts_strogatz", "barabasi_albert"])
        beta = 0.15
        p_base_mode = "empirical"
        policy = st.selectbox("Policy", ["Fixed", "Target-seeking dynamic"])
    
    # ==========================================
    # HEADER
    # ==========================================
    st.title("Sangam Vidyut: Interactive Research Dashboard")
    st.markdown("Explore nonlinear residential rooftop-solar adoption under household heterogeneity, social-network diffusion, and finite policy feedback loops.")
    
    # ==========================================
    # DYNAMIC METRICS (KPIs)
    # ==========================================
    if phase == "Phase 4F.1" and not df1.empty:
        df_abm = df1[(df1["topology"] == topology) & 
                     (df1["beta"] == beta) & 
                     (df1["p_base_mode"] == p_base_mode) &
                     (df1["model_class"] == "DETERMINISTIC_EMPIRICAL_ABM")].copy()
        
        if df_abm.empty:
            st.warning("Selected factor combination is not available in this phase.")
        else:
            st.markdown(f"**Scope**: topology=`{topology}`, beta=`{beta}`, household=`{p_base_mode}`")
            if df_abm["subsidy"].nunique() <= 1:
                st.info("Only one subsidy level was tested for this exact configuration in Phase 4F.1.")
            df_abm["adoption_pct"] = (df_abm["final_adoption"] / 500.0) * 100
            fig = px.box(df_abm, x="subsidy", y="adoption_pct", title="Adoption Distribution Across Available Subsidies")
            st.plotly_chart(fig, use_container_width=True)
    elif phase == "Phase 4F.2" and not df2.empty:
        df_abm = df2[(df2["topology"] == topology) & 
                     (df2["beta"] == beta) & 
                     (df2["p_base_mode"] == p_base_mode) &
                     (df2["model_class"] == "DETERMINISTIC_EMPIRICAL_ABM")].copy()
        
        if df_abm.empty:
            st.warning("Selected factor combination is not available in this phase.")
        else:
            st.markdown(f"**Scope**: topology=`{topology}`, beta=`{beta}`, household=`{p_base_mode}`")
            if df_abm["subsidy"].nunique() <= 1:
                st.info("Only one subsidy level was tested for this exact configuration.")
            df_abm["adoption_pct"] = df_abm["mean_adoption_pct"] * 100
            fig = px.box(df_abm, x="subsidy", y="adoption_pct", title="Adoption Distribution Across Available Subsidies")
            st.plotly_chart(fig, use_container_width=True)
    elif phase == "Phase 4F.3":
        is_dyn = (policy == "Target-seeking dynamic")
        traj = load_trajectory(subsidy, topology, is_dyn)
    
        if not traj.empty:
            st.markdown(f"**Data for exact selection**: policy=`{policy}`, subsidy=`{subsidy}`, topology=`{topology}`")
            traj["Policy"] = policy
            fig = px.line(traj, x="quarter", y="adoption_count", color="Policy", title=f"Adoption Trajectory (Subsidy {subsidy}, {policy})")
            fig.add_hline(y=250, line_dash="dash", line_color="red", annotation_text="50% Target")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Selected factor combination is not available in this phase.")
    
    # ==========================================
    # FACTOR COMPARISON PANELS
    # ==========================================
    st.divider()
    st.header("Factor Comparison (OBSERVED MODEL REGIMES)")
    
    if phase in ["Phase 4F.1", "Phase 4F.2"]:
        c1, c2 = st.columns(2)
        
        if phase == "Phase 4F.1":
            df_comp = df1[df1["model_class"] == "DETERMINISTIC_EMPIRICAL_ABM"].copy()
            df_comp["adoption_pct"] = (df_comp["final_adoption"] / 500.0) * 100
        else:
            df_comp = df2[df2["model_class"] == "DETERMINISTIC_EMPIRICAL_ABM"].copy()
            df_comp["adoption_pct"] = df_comp["mean_adoption_pct"] * 100

        with c1:
            st.subheader("Subsidy Response Panel")
            st.markdown("**Scope**: All topologies × All beta values × All household modes")
            agg_df = df_comp.groupby("subsidy")["adoption_pct"].mean().reset_index()
            if len(agg_df) > 1:
                fig2 = px.line(agg_df, x="subsidy", y="adoption_pct", markers=True)
                if phase == "Phase 4F.2":
                    fig2.add_vrect(x0=-100, x1=2000, fillcolor="red", opacity=0.1, annotation_text="AFFORDABILITY-BLOCKED")
                    fig2.add_vrect(x0=2000, x1=3000, fillcolor="orange", opacity=0.1, annotation_text="DIFFUSION-ACTIVE")
                    fig2.add_vrect(x0=3000, x1=5100, fillcolor="green", opacity=0.1, annotation_text="SATURATED")
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("Insufficient subsidy variation in data to plot response curve.")
                
        with c2:
            st.subheader("Topology Panel")
            st.markdown("**Scope**: All beta values × All household modes (grouped by topology)")
            agg_top = df_comp.groupby(["subsidy", "topology"])["adoption_pct"].mean().reset_index()
            if len(agg_top) > 0:
                fig_top = px.bar(agg_top, x="subsidy", y="adoption_pct", color="topology", barmode="group")
                st.plotly_chart(fig_top, use_container_width=True)
            else:
                st.warning("No data available.")

        c3, c4 = st.columns(2)
        with c3:
            st.subheader("Beta Panel")
            st.markdown("**Scope**: All topologies × All household modes (grouped by beta)")
            agg_beta = df_comp.groupby(["subsidy", "beta"])["adoption_pct"].mean().reset_index()
            # Convert beta back to string if it was float so plotly handles it as discrete color correctly
            agg_beta["beta"] = agg_beta["beta"].astype(str)
            if len(agg_beta) > 0:
                fig_beta = px.line(agg_beta, x="subsidy", y="adoption_pct", color="beta", markers=True)
                st.plotly_chart(fig_beta, use_container_width=True)
            else:
                st.warning("No data available.")
                
        with c4:
            st.subheader("Heterogeneity Panel")
            st.markdown(f"**Scope**: topology=`{topology}`, beta=`{beta}` (grouped by household mode)")
            df_het = df_comp[(df_comp["topology"] == topology) & (df_comp["beta"] == beta)].copy()
            if df_het.empty:
                st.warning("No validated result for this exact topology and beta combination.")
            else:
                agg_het = df_het.groupby(["subsidy", "p_base_mode"])["adoption_pct"].mean().reset_index()
                if agg_het["subsidy"].nunique() <= 1:
                    st.info(f"Only one subsidy level exists for topology={topology}, beta={beta}. Line chart unavailable.")
                    fig_het = px.scatter(agg_het, x="subsidy", y="adoption_pct", color="p_base_mode", size_max=10)
                    st.plotly_chart(fig_het, use_container_width=True)
                else:
                    fig_het = px.line(agg_het, x="subsidy", y="adoption_pct", color="p_base_mode", markers=True)
                    st.plotly_chart(fig_het, use_container_width=True)

    else:
        st.info("Factor Analysis panels apply to sweeping mechanisms (4F.1, 4F.2). Phase 4F.3 isolates budget expenditure (see below).")
    st.divider()
    st.header("The Budget Paradox Panel")
    if phase == "Phase 4F.3":
        st.info("**Observed mechanism in the Sangam Vidyut model under the tested configuration** (Not a general economic law)")
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("### Path A: Rapid Early Adoption")
            st.markdown("Faster subsidy expenditure ➔ earlier budget exhaustion ➔ subsidy collapse ➔ delayed/halted cascade.")
        with col_b:
            st.markdown("### Path B: Slower Early Adoption")
            st.markdown("Budget preservation ➔ continued price decline ➔ later affordability improvement ➔ mass delayed adoption.")
    
        st.markdown("#### Fixed vs Dynamic Comparison")
        t_fixed = load_trajectory(subsidy, topology, False)
        t_dyn = load_trajectory(subsidy, topology, True)
        if not t_fixed.empty and not t_dyn.empty:
            t_fixed["Policy"] = "Fixed"
            t_dyn["Policy"] = "Dynamic"
            combined = pd.concat([t_fixed, t_dyn])
            fig_both = px.line(combined, x="quarter", y="adoption_count", color="Policy", title=f"Adoption Trajectory (Fixed vs Dynamic, Subsidy {subsidy})")
            fig_both.add_hline(y=250, line_dash="dash", line_color="red", annotation_text="50% Target")
            st.plotly_chart(fig_both, use_container_width=True)
    else:
        st.info("The Budget Paradox Panel relies on Phase 4F.3 data. Switch to Phase 4F.3 to view.")
    
    # ==========================================
    # COGNITIVE LAYER & ARCHITECTURE
    # ==========================================
    st.divider()
    st.header("Architecture & Cognitive Layer")
    col_arch, col_cog = st.columns(2)
    with col_arch:
        st.image("docs/figures/figure_01_architecture.png", use_container_width=True)
        st.caption("Built with Mesa, NetworkX, and LangGraph.")
    with col_cog:
        st.subheader("Hybrid Cognitive Routing")
        st.markdown("*The LLM is used as an ambiguity-routing component. No aggregate cognitive adoption advantage was detected in the tested configuration.*")
        st.markdown("- **Provider**: MockLLM (Seed isolated)")
        st.markdown("- **Total Evaluations**: 1,163,720")
        st.markdown("- **Cache Hits**: 299,321 (0 cross-seed contamination)")
        
    # ==========================================
    # DATA & CALIBRATION
    # ==========================================
    st.divider()
    st.header("Data & Calibration")
    st.markdown("Empirical inputs include HCES 2023-24, MNRE/PM Surya Ghar targets, CEA limits, and MNRE benchmark costs. **Calibration is aggregate-consistent/ecological rather than causal household-level identification.**")
    
    # ==========================================
    # EVIDENCE BADGES
    # ==========================================
    st.divider()
    st.header("Results / Evidence Badges")
    badges_c1, badges_c2, badges_c3 = st.columns(3)
    with badges_c1:
        st.success("Q1 ABM vs Static: SUPPORTED")
        st.warning("Q2 Topology: CONDITIONALLY_SUPPORTED")
        st.warning("Q3 Beta: CONDITIONALLY_SUPPORTED")
    with badges_c2:
        st.warning("Q4 Heterogeneity: CONDITIONALLY_SUPPORTED")
        st.success("Q5 Subsidy: SUPPORTED")
        st.error("Q6 Cognitive: NOT_SUPPORTED")
    with badges_c3:
        st.success("H1: SUPPORTED")
        st.warning("H2: CONDITIONALLY_SUPPORTED")
        st.error("H3: NOT_SUPPORTED")
    
    # ==========================================
    # METHODOLOGY & LIMITATIONS
    # ==========================================
    st.divider()
    with st.expander("Methodology & Reproducibility"):
        st.markdown("- **Random Seeds**: 10 matched seeds `[42...51]`")
        st.markdown("- **Experiment Counts**: Phase 4F.1 (180 runs), Phase 4F.2 (560 runs), Phase 4F.3 (320 runs)")
        st.markdown("- **Calibration Hash**: `SHA-256: 0d5acf7...`")
        st.markdown("- **Test Count**: 126 tests passed guaranteeing SIR invariants and persistence.")
    
    st.markdown("### Limitations")
    st.caption("- N=500, ecological calibration, synthetic networks.\n- Beta not empirically calibrated.\n- Target-seeking policy is a model heuristic.\n- MockLLM limitations apply.\n- No causal claims.")

def render_live_simulation():
    st.header("Live Simulation Configuration")
    
    with st.form("live_sim_form"):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            subsidy = st.number_input("Subsidy Level", value=1000.0, step=100.0)
            beta = st.number_input("Beta (Transmission)", value=0.15, step=0.01)
            population = st.number_input("Population", value=500, step=50, min_value=10)
            
        with col2:
            horizon = st.number_input("Simulation Horizon (Quarters)", value=24, step=4, min_value=4)
            budget = st.number_input("Government Budget", value=1000000.0, step=10000.0)
            initial_adoption = st.number_input("Initial Adoption", value=5, step=1)
            seed = st.number_input("Random Seed", value=42, step=1)
            recovery = st.number_input("Recovery Rate (Quarters)", value=2, step=1)
            
        with col3:
            topology = st.selectbox("Topology", ["watts_strogatz", "barabasi_albert"])
            household = st.selectbox("Household Representation", ["empirical", "constant"])
            policy = st.selectbox("Policy Mode", ["fixed", "dynamic"])
            
        with col4:
            cognitive = st.selectbox("Cognitive Mode", ["deterministic", "mock", "ollama"])
            
        submitted = st.form_submit_button("Run Simulation", type="primary")
        
    if submitted:
        if population > 5000:
            st.warning("Large population selected. Simulation may take a while.")
        
        runner = LiveSimulationRunner(
            subsidy=subsidy,
            beta=beta,
            population=population,
            horizon=horizon,
            budget=budget,
            initial_adoption=initial_adoption,
            recovery=recovery,
            seed=seed,
            topology=topology,
            household_mode=household,
            policy_mode=policy,
            cognitive_mode=cognitive
        )
        
        with st.spinner("Executing simulation..."):
            try:
                result = runner.run()
                st.session_state["live_result"] = result
            except Exception as e:
                st.error(f"Simulation failed: {e}")
                
    if "live_result" in st.session_state:
        res = st.session_state["live_result"]
        st.success(f"LIVE RUN | Run ID: {res['run_id']} | Runtime: {res['execution_time']:.2f} s")
        
        st.markdown(f"**Configuration:** Seed: {res['config'].simulation.seed} | Subsidy: ₹{res['config'].government.base_subsidy} | Beta: {res['config'].sir.beta} | Population: {res['config'].simulation.n_agents} | Horizon: {res['config'].simulation.timesteps} | Topology: {res['config'].network.topology} | Households: {res['config'].simulation.baseline_provider} | Policy: {'Dynamic' if res['config'].government.dynamic_subsidy else 'Fixed'} | Cognitive: {cognitive}")
        
        df = res["df"]
        
        st.subheader("Key Performance Indicators")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Final Adoption Count", df["adoption_count"].iloc[-1])
        c2.metric("Final Adoption %", f"{df['adoption_count'].iloc[-1] / res['config'].simulation.n_agents * 100:.1f}%")
        c3.metric("Total Subsidy Expenditure", f"₹{df['cumulative_expenditure'].iloc[-1]:.0f}")
        c4.metric("Remaining Budget", f"₹{df['budget_remaining'].iloc[-1]:.0f}")
        
        c5, c6, c7, c8 = st.columns(4)
        c5.metric("Final Industry Price", f"₹{df['panel_price'].iloc[-1]:.0f}")
        c6.metric("Total Rule Decisions", res["metrics"]["rule_decisions"])
        c7.metric("LLM Provider Calls", res["metrics"]["call_count"])
        c8.metric("CO2 Avoided (Tons)", f"{df['estimated_emissions_reduction'].iloc[-1]:.1f}")
        
        st.subheader("Interactive Plots")
        
        fig1 = px.line(df, x="timestep", y=["adoption_count", "new_adoptions"], title="Adoption Dynamics")
        st.plotly_chart(fig1, use_container_width=True)
        
        fig2 = px.line(df, x="timestep", y=["susceptible_count", "infected_count", "recovered_count"], title="SIR Diffusion")
        st.plotly_chart(fig2, use_container_width=True)
        
        fig3 = px.line(df, x="timestep", y=["subsidy", "panel_price"], title="Economic Feedback (Prices)")
        st.plotly_chart(fig3, use_container_width=True)
        
        fig4 = px.line(df, x="timestep", y=["budget_remaining", "cumulative_expenditure"], title="Government Budget")
        st.plotly_chart(fig4, use_container_width=True)

tab_live, tab_locked = st.tabs(["LIVE SIMULATION", "LOCKED RESEARCH RESULTS"])
with tab_live:
    render_live_simulation()
with tab_locked:
    st.info("These are archived runs from the 1,060 experiment campaign.")
    render_locked_research_results()
