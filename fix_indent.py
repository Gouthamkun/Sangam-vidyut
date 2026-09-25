with open("app.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if line.startswith('        elif phase == "Phase 4F.2" and not df2.empty:'):
        # unindent it back to match `if phase == "Phase 4F.1"`
        new_lines.append('    elif phase == "Phase 4F.2" and not df2.empty:\n')
    else:
        new_lines.append(line)

with open("app.py", "w", encoding="utf-8") as f:
    f.writelines(new_lines)
