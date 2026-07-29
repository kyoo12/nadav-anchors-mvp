with open("extract_segmented.py", "r", encoding="utf-8") as f:
    code = f.read()

# Make sure it's a dict!
if "pillars_data = []" in code:
    code = code.replace("pillars_data = []", "pillars_data = {}")

with open("extract_segmented.py", "w", encoding="utf-8") as f:
    f.write(code)
