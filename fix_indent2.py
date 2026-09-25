with open("app.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

for j in range(130, 139):
    if j < len(lines):
        if not lines[j].strip() == "":
            lines[j] = "    " + lines[j]

with open("app.py", "w", encoding="utf-8") as f:
    f.writelines(lines)
