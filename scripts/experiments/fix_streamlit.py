with open("app.py", "r") as f:
    text = f.read()

text = text.replace("use_column_width=True", "width=\"stretch\"")
text = text.replace("use_container_width=True", "width=\"stretch\"")
text = text.replace("use_container_width=False", "width=\"content\"")

with open("app.py", "w") as f:
    f.write(text)
