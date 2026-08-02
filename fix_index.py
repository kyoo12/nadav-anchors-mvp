with open("extract_segmented.py", "r", encoding="utf-8") as f:
    script = f.read()

script = script.replace("floor_group = [col[f_idx] for col in columns]",
                        "floor_group = [col[f_idx] for col in columns if f_idx < len(col)]")

with open("extract_segmented.py", "w", encoding="utf-8") as f:
    f.write(script)
