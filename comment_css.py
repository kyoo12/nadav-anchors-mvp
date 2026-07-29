with open("web/src/index.css", "r", encoding="utf-8") as f:
    content = f.read()

docstring = """/*
 * index.css
 * 
 * Global stylesheet implementing the Tablet-First UI/UX overhaul.
 * Design Pattern: "Hero-Centric + Exaggerated Minimalism"
 * Key Features:
 * - Cinzel & Josefin Sans font pairing
 * - Blueprint Blue (#3B82F6) & Safety Orange (#F97316) color scheme
 * - Heavy glassmorphism (12px backdrop blur)
 * - Minimum 48px touch targets for Galaxy Tab Ultra compatibility
 */
"""

if not content.startswith('/*'):
    content = docstring + content

with open("web/src/index.css", "w", encoding="utf-8") as f:
    f.write(content)
