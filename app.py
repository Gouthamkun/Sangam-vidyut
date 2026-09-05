import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Sangam Vidyut Research Dashboard", layout="wide")

# ==========================================
# CACHED DATA LOADERS
# ==========================================
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
    # R3_DET_{subsidy}_{is_dynamic}_{topology}_42_trajectory.csv
    # e.g. R3_DET_3000.0_False_watts_strogatz_42_trajectory.csv
    dyn_str = "True" if is_dynamic else "False"
    path = f"outputs/experiments/phase_4f_3/raw/R3_DET_{subsidy}_{dyn_str}_{topology}_42_trajectory.csv"
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame()

# Load primary datasets
df2 = load_phase2_data()
df3 = load_phase3_data()

# ==========================================
# SIDEBAR
# ==========================================
st.sidebar.title("Sangam Vidyut")
st.sidebar.markdown("**MODEL SIMULATION**")
st.sidebar.markdown("*This dashboard visualizes results from a bounded computational experiment. It is not a validated national forecast.*")

st.sidebar.header("Controls")
phase = st.sidebar.radio("Research Phase", ["Phase 4F.1", "Phase 4F.2", "Phase 4F.3"])

subsidy_options = [0.0, 1000.0, 2000.0, 3000.0, 4000.0, 5000.0]
subsidy = st.sidebar.selectbox("Subsidy Level", subsidy_options, index=3)

topology = st.sidebar.selectbox("Topology", ["watts_strogatz", "barabasi_albert"])
beta = st.sidebar.selectbox("Beta (Transmission)", [0.05, 0.15, 0.3])
p_base_mode = st.sidebar.selectbox("Household Representation", ["empirical", "constant"])
policy = st.sidebar.selectbox("Policy", ["Fixed", "Target-seeking dynamic"])

# ==========================================
# HEADER
# ==========================================
st.title("Sangam Vidyut: Interactive Research Dashboard")
st.markdown("Explore nonlinear residential rooftop-solar adoption under household heterogeneity, social-network diffusion, and finite policy feedback loops.")

# ==========================================
# DYNAMIC METRICS
# ==========================================
if phase == "Phase 4F.2" and not df2.empty:
    subset = df2[(df2["subsidy"] == subsidy) & 
                 (df2["topology"] == topology) & 
                 (df2["beta"] == beta) & 
                 (df2["p_base_mode"] == p_base_mode) &
                 (df2["model_class"] == "DETERMINISTIC_EMPIRICAL_ABM")]
    
    if not subset.empty:
        st.subheader("Model KPIs (Phase 4F.2)")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Final Adoption %", f"{subset.iloc[0]['mean_adoption_pct']*100:.1f}%")
        c2.metric("Mean Final Count", f"{subset.iloc[0]['mean_adoption_count']:.0f}")
        c3.metric("Tipping Freq", f"{subset.iloc[0]['tipping_freq']*100:.0f}%")
        c4.metric("Mean Peak New", f"{subset.iloc[0]['mean_peak_new']:.0f}")
    else:
        st.warning("Factor combination not available in Phase 4F.2 dataset.")

elif phase == "Phase 4F.3" and not df3.empty:
    st.subheader("Model KPIs (Phase 4F.3)")
    is_dyn = (policy == "Target-seeking dynamic")
    traj = load_trajectory(subsidy, topology, is_dyn)
    if not traj.empty:
        final_row = traj.iloc[-1]
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Final Adoption Count", f"{final_row['adoption_count']:.0f} / 500")
        c2.metric("Total Expenditure", f"₹{1000000 - final_row['budget_remaining']:.0f}")
        c3.metric("Budget Remaining", f"₹{final_row['budget_remaining']:.0f}")
        c4.metric("Time to 50%", f"Quarter {traj[traj['adoption_count'] >= 250]['quarter'].min() if (traj['adoption_count'] >= 250).any() else 'N/A'}")
    else:
        st.warning("Selected trajectory not available.")

# ==========================================
# MAIN ADOPTION CHART
# ==========================================
st.divider()
st.header("Main Adoption Chart")

if phase == "Phase 4F.3":
    st.markdown("Comparing Fixed vs Target-seeking dynamic policy for the selected configuration.")
    t_fixed = load_trajectory(subsidy, topology, False)
    t_dyn = load_trajectory(subsidy, topology, True)
    
    if not t_fixed.empty and not t_dyn.empty:
        t_fixed["Policy"] = "Fixed"
        t_dyn["Policy"] = "Dynamic"
        combined = pd.concat([t_fixed, t_dyn])
        fig = px.line(combined, x="quarter", y="adoption_count", color="Policy", title=f"Adoption Trajectory (Subsidy {subsidy})")
        fig.add_hline(y=250, line_dash="dash", line_color="red", annotation_text="50% Target")
        st.plotly_chart(fig, width="stretch")

elif phase == "Phase 4F.2" and not df2.empty:
    st.markdown("Showing final adoption responses across subsidies.")
    df_abm = df2[df2["model_class"] == "DETERMINISTIC_EMPIRICAL_ABM"].copy()
    df_abm["adoption_pct"] = df_abm["mean_adoption_pct"] * 100
    fig = px.box(df_abm, x="subsidy", y="adoption_pct", title="Adoption Distribution Across Subsidies")
    st.plotly_chart(fig, width="stretch")

# ==========================================
# ANALYSIS PANELS
# ==========================================
st.divider()
st.header("Factor Analysis (OBSERVED MODEL REGIMES)")
c1, c2 = st.columns(2)

with c1:
    st.subheader("Subsidy Response Panel")
    if not df2.empty:
        df_abm = df2[df2["model_class"] == "DETERMINISTIC_EMPIRICAL_ABM"].copy()
        df_abm["adoption_pct"] = df_abm["mean_adoption_pct"] * 100
        fig2 = px.line(df_abm.groupby("subsidy")["adoption_pct"].mean().reset_index(), x="subsidy", y="adoption_pct", markers=True)
        fig2.add_vrect(x0=-100, x1=2000, fillcolor="red", opacity=0.1, annotation_text="AFFORDABILITY-BLOCKED")
        fig2.add_vrect(x0=2000, x1=3000, fillcolor="orange", opacity=0.1, annotation_text="DIFFUSION-ACTIVE")
        fig2.add_vrect(x0=3000, x1=5100, fillcolor="green", opacity=0.1, annotation_text="SATURATED")
        st.plotly_chart(fig2, width="stretch")
        
with c2:
    st.subheader("Topology Panel")
    st.markdown("*Topology effects emerge in diffusion-active conditions in the tested parameterization.*")
    if not df2.empty:
        fig_top = px.bar(df_abm.groupby(["subsidy", "topology"])["adoption_pct"].mean().reset_index(), x="subsidy", y="adoption_pct", color="topology", barmode="group")
        st.plotly_chart(fig_top, width="stretch")

c3, c4 = st.columns(2)
with c3:
    st.subheader("Beta Panel")
    st.markdown("*β controls the modeled transmission strength of social influence.*")
    if not df2.empty:
        fig_beta = px.line(df_abm.groupby(["subsidy", "beta"])["adoption_pct"].mean().reset_index(), x="subsidy", y="adoption_pct", color="beta", markers=True)
        st.plotly_chart(fig_beta, width="stretch")
        
with c4:
    st.subheader("Heterogeneity Panel")
    st.markdown("*Conditional variance impact between Empirical vs Constant households.*")
    if not df2.empty:
        df_het = df2[(df2["topology"] == "watts_strogatz") & (df2["beta"] == 0.15)].copy()
        df_het["adoption_pct"] = df_het["mean_adoption_pct"] * 100
        fig_het = px.line(df_het, x="subsidy", y="adoption_pct", color="p_base_mode", markers=True)
        st.plotly_chart(fig_het, width="stretch")

# ==========================================
# BUDGET PARADOX (Phase 4F.3)
# ==========================================
st.divider()
st.header("The Budget Paradox Panel")
st.info("**Observed mechanism in the Sangam Vidyut model under the tested configuration** (Not a general economic law)")
col_a, col_b = st.columns(2)
with col_a:
    st.markdown("### Path A: Rapid Early Adoption")
    st.markdown("Faster subsidy expenditure → earlier budget exhaustion → subsidy collapse → delayed/halted cascade.")
with col_b:
    st.markdown("### Path B: Slower Early Adoption")
    st.markdown("Budget preservation → continued price decline → later affordability improvement → mass delayed adoption.")

# ==========================================
# COGNITIVE LAYER & ARCHITECTURE
# ==========================================
st.divider()
st.header("Architecture & Cognitive Layer")
col_arch, col_cog = st.columns(2)
with col_arch:
    st.image("docs/figures/figure_01_architecture.png", width="stretch")
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
    st.markdown("- **Experiment Counts**: Phase 4F.2 (560 runs), Phase 4F.3 (320 runs)")
    st.markdown("- **Calibration Hash**: `SHA-256: 0d5acf7...`")
    st.markdown("- **Test Count**: 126 tests passed guaranteeing SIR invariants and persistence.")

st.markdown("### Limitations")
st.caption("- N=500, ecological calibration, synthetic networks.\n- Beta not empirically calibrated.\n- Target-seeking policy is a model heuristic.\n- MockLLM limitations apply.\n- No causal claims.")

