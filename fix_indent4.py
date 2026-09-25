with open("app.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

lines[138] = "            st.plotly_chart(fig, use_container_width=True)\n"

with open("app.py", "w", encoding="utf-8") as f:
    f.writelines(lines)
