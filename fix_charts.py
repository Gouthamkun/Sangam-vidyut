import re

with open("app.py", "r", encoding="utf-8") as f:
    code = f.read()

# We need to replace the factor comparison logic with proper scoping and error handling
def replace_between(text, start_str, end_str, replacement):
    start_idx = text.find(start_str)
    end_idx = text.find(end_str, start_idx)
    if start_idx != -1 and end_idx != -1:
        return text[:start_idx] + replacement + text[end_idx:]
    return text

new_main_chart_phase1 = """    if phase == "Phase 4F.1" and not df1.empty:
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
    """

new_main_chart_phase2 = """    elif phase == "Phase 4F.2" and not df2.empty:
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
    """

new_factor_comparison = """    st.header("Factor Comparison (OBSERVED MODEL REGIMES)")
    
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
"""

# Replace Main adoption chart
s1 = '    if phase == "Phase 4F.1" and not df1.empty:'
e1 = '    elif phase == "Phase 4F.3":'
code = replace_between(code, s1, e1, new_main_chart_phase1 + new_main_chart_phase2)

# Replace Factor Comparison
s2 = '    st.header("Factor Comparison (OBSERVED MODEL REGIMES)")'
e2 = '    st.divider()\n    st.header("The Budget Paradox Panel")'
code = replace_between(code, s2, e2, new_factor_comparison)

# Fix plot width
code = code.replace('width="stretch"', 'use_container_width=True')

with open("app.py", "w", encoding="utf-8") as f:
    f.write(code)
