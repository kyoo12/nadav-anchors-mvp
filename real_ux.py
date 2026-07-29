with open("web/src/index.css", "r", encoding="utf-8") as f:
    css = f.read()

# 1. Much more transparent glassmorphism for that premium feel
css = css.replace(
    """  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.5);
  border-radius: 16px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);""",
    """  background: rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border: 1px solid rgba(255, 255, 255, 0.4);
  border-right: 1px solid rgba(255, 255, 255, 0.2);
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 24px;
  box-shadow: 0 30px 60px rgba(0, 0, 0, 0.12);"""
)

# 2. Update Floor Toggles to be dramatic
css = css.replace(
    """.floor-toggle {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px; min-height: 56px;
  background: #f8fafc;
  border: 1px solid var(--border-glass);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.floor-toggle:hover {
  background: #f1f5f9;
}

.floor-toggle.active {
  border-color: var(--accent-blue);
  background: #eff6ff;
}""",
    """.floor-toggle {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px; min-height: 56px;
  background: rgba(255, 255, 255, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.5);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.02);
}

.floor-toggle:hover {
  background: rgba(255, 255, 255, 0.7);
  transform: translateY(-2px);
  box-shadow: 0 8px 12px rgba(0, 0, 0, 0.05);
}

.floor-toggle.active {
  border: 2px solid var(--accent-cyan);
  background: var(--text-main);
  color: white;
}
.floor-toggle.active .toggle-count {
  background: var(--accent-cyan);
  color: white;
}"""
)

# 3. Dramatic header
css = css.replace(
    """  font-family: 'Cinzel', serif;
  font-size: 1.75rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  margin-bottom: 8px;
  background: linear-gradient(to right, var(--accent-blue), var(--accent-cyan));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;""",
    """  font-family: 'Cinzel', serif;
  font-size: 2.2rem;
  font-weight: 900;
  letter-spacing: -0.05em;
  margin-bottom: 4px;
  text-transform: uppercase;
  color: var(--text-main);"""
)

# Fix sidebar width and padding
css = css.replace(
    "  width: 340px;",
    "  width: 380px;"
)

with open("web/src/index.css", "w", encoding="utf-8") as f:
    f.write(css)

# Now App.tsx for the canvas background!
with open("web/src/App.tsx", "r", encoding="utf-8") as f:
    app = f.read()

# Change canvas background to a deeper blueprint color so the white glass POPS
app = app.replace(
    "<color attach=\"background\" args={['#f1f5f9']} />",
    "<color attach=\"background\" args={['#dbeafe']} />" # Light blue slate, makes UI pop
)

# Fix the "Hide All" button to look premium
app = app.replace(
    "background: 'none', border: 'none', color: 'var(--accent-blue)',",
    "background: 'var(--accent-blue)', border: 'none', color: 'white', borderRadius: '12px', padding: '0 16px', fontWeight: 600,"
)

with open("web/src/App.tsx", "w", encoding="utf-8") as f:
    f.write(app)
