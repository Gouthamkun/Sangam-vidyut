with open("app.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

# Line 211 is `    else:\n`
lines.insert(212, '        st.info("Factor Analysis panels apply to sweeping mechanisms (4F.1, 4F.2). Phase 4F.3 isolates budget expenditure (see below).")\n')

with open("app.py", "w", encoding="utf-8") as f:
    f.writelines(lines)
