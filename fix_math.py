import re

with open("extract_segmented.py", "r", encoding="utf-8") as f:
    code = f.read()

# Remove the inner import math
code = code.replace("    import math\n", "")
# Add import math at the top
if "import math" not in code:
    code = "import math\n" + code

with open("extract_segmented.py", "w", encoding="utf-8") as f:
    f.write(code)
