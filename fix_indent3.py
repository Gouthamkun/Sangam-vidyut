with open("app.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

for j in range(129, 138):
    if lines[j].startswith("        "):
        lines[j] = lines[j][4:]

with open("app.py", "w", encoding="utf-8") as f:
    f.writelines(lines)
