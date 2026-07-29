with open("web/src/index.css", "r", encoding="utf-8") as f:
    css = f.read()

# Replace variables with dark mode
css = css.replace("--bg-dark: #f1f5f9;", "--bg-dark: #020617;")
css = css.replace("--bg-panel: #ffffff;", "--bg-panel: #0f172a;")
css = css.replace("--border-glass: #e2e8f0;", "--border-glass: #1e293b;")
css = css.replace("--accent-blue: #3B82F6;", "--accent-blue: #00F0FF;") # Neon Cyan
css = css.replace("--accent-cyan: #F97316;", "--accent-cyan: #B026FF;") # Electric Purple
css = css.replace("--text-main: #1E293B;", "--text-main: #F8FAFC;") # White
css = css.replace("--text-muted: #475569;", "--text-muted: #94A3B8;") # Silver

css = css.replace("font-family: 'Josefin Sans', sans-serif;", "font-family: 'Outfit', sans-serif;")

# Replace glassmorphism with dark glass
css = css.replace(
    """  background: rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border: 1px solid rgba(255, 255, 255, 0.4);
  border-right: 1px solid rgba(255, 255, 255, 0.2);
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);""",
    """  background: rgba(15, 23, 42, 0.7);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border: 1px solid rgba(99, 102, 241, 0.3);
  border-right: 1px solid rgba(99, 102, 241, 0.1);
  border-bottom: 1px solid rgba(99, 102, 241, 0.1);"""
)

# Header font
css = css.replace(
    """  font-family: 'Cinzel', serif;
  font-size: 2.2rem;
  font-weight: 900;
  letter-spacing: -0.05em;
  margin-bottom: 4px;
  text-transform: uppercase;
  color: var(--text-main);""",
    """  font-family: 'Outfit', sans-serif;
  font-size: 2.2rem;
  font-weight: 800;
  letter-spacing: -0.02em;
  margin-bottom: 4px;
  text-transform: uppercase;
  background: linear-gradient(135deg, var(--text-main), var(--text-muted));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;"""
)

# Floor toggles (sleek dark)
css = css.replace(
    """  background: rgba(255, 255, 255, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.5);""",
    """  background: rgba(30, 41, 59, 0.5);
  border: 1px solid rgba(51, 65, 85, 0.8);"""
)

css = css.replace(
    """  background: rgba(255, 255, 255, 0.7);""",
    """  background: rgba(51, 65, 85, 0.8);"""
)

css = css.replace(
    """  border: 2px solid var(--accent-cyan);
  background: var(--text-main);
  color: white;""",
    """  border: 1px solid var(--accent-blue);
  background: rgba(0, 240, 255, 0.1);
  color: var(--text-main);
  box-shadow: 0 0 15px rgba(0, 240, 255, 0.2) inset, 0 0 10px rgba(0, 240, 255, 0.2);"""
)

css = css.replace(
    """  background: var(--accent-cyan);
  color: white;""",
    """  background: var(--accent-blue);
  color: #020617;
  font-family: 'Roboto Mono', monospace;
  font-weight: bold;"""
)

# Monospace tags
css = css.replace(
    """  font-family: monospace;""",
    """  font-family: 'Roboto Mono', monospace;"""
)
css = css.replace(
    """  color: #0f172a;""",
    """  color: var(--text-main);"""
)

# Detail section
css = css.replace(
    """  background: #f8fafc;
  border: 1px solid #e2e8f0;""",
    """  background: rgba(30, 41, 59, 0.5);
  border: 1px solid rgba(51, 65, 85, 0.8);"""
)

# Tooltip 
css = css.replace(
    """  border-bottom: 1px solid #e2e8f0;""",
    """  border-bottom: 1px solid rgba(99, 102, 241, 0.2);"""
)

# Scrollbar 
css = css.replace(
    """  background: #cbd5e1;""",
    """  background: rgba(148, 163, 184, 0.3);"""
)
css = css.replace(
    """  background: #94a3b8;""",
    """  background: rgba(148, 163, 184, 0.5);"""
)


with open("web/src/index.css", "w", encoding="utf-8") as f:
    f.write(css)

with open("web/src/App.tsx", "r", encoding="utf-8") as f:
    app = f.read()

# Replace fonts
app = app.replace(
    "family=Cinzel:wght@400;500;600;700&family=Josefin+Sans:wght@300;400;500;600;700",
    "family=Outfit:wght@300;400;500;600;700;800;900&family=Roboto+Mono:wght@400;500;600;700"
)

# Replace canvas background
app = app.replace(
    "<color attach=\"background\" args={['#dbeafe']} />",
    "<color attach=\"background\" args={['#020617']} />" # Deep midnight slate
)

with open("web/src/App.tsx", "w", encoding="utf-8") as f:
    f.write(app)
