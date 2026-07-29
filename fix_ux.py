with open("web/src/index.css", "r", encoding="utf-8") as f:
    css = f.read()

# Update root variables
css = css.replace(
    "--accent-blue: #1d4ed8;",
    "--accent-blue: #3B82F6;"
)
css = css.replace(
    "--accent-cyan: #ea580c;",
    "--accent-cyan: #F97316;" # Using orange as secondary/CTA
)
css = css.replace(
    "--text-main: #0f172a;",
    "--text-main: #1E293B;"
)
css = css.replace(
    "font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;",
    "font-family: 'Josefin Sans', sans-serif;"
)

# Update glassmorphism
css = css.replace(
    """  background: var(--bg-panel);
  border: 1px solid var(--border-glass);
  border-radius: 16px;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1);""",
    """  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.5);
  border-radius: 16px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);"""
)

# Update typography for headers
css = css.replace(
    """  font-size: 1.5rem;
  font-weight: 700;""",
    """  font-family: 'Cinzel', serif;
  font-size: 1.75rem;
  font-weight: 700;
  letter-spacing: -0.02em;"""
)

# Tablet padding for sidebar
css = css.replace(
    """  width: 320px;
  max-height: calc(100vh - 40px);""",
    """  width: 340px;
  max-height: calc(100vh - 40px);"""
)

# Touch targets
css = css.replace(
    """  padding: 16px; min-height: 48px;""",
    """  padding: 16px; min-height: 56px;"""
)

# Button styling
css = css.replace(
    "cursor: 'pointer', fontSize: '0.9rem'",
    "cursor: 'pointer', fontSize: '1rem', padding: '8px 12px', minHeight: '44px'"
)

with open("web/src/index.css", "w", encoding="utf-8") as f:
    f.write(css)


with open("web/src/App.tsx", "r", encoding="utf-8") as f:
    app = f.read()

# Add google fonts import to the top of App.tsx (we can inject it into document.head via useEffect or just return a <style> tag)
style_tag = """
function App() {
  useEffect(() => {
    const link = document.createElement('link');
    link.href = 'https://fonts.googleapis.com/css2?family=Cinzel:wght@400;500;600;700&family=Josefin+Sans:wght@300;400;500;600;700&display=swap';
    link.rel = 'stylesheet';
    document.head.appendChild(link);
    return () => { document.head.removeChild(link); }
  }, []);
"""
app = app.replace("function App() {", style_tag)

# Update buttons with touch targets
app = app.replace(
    "fontSize: '0.9rem'",
    "fontSize: '1rem', minHeight: '44px', minWidth: '44px', display: 'flex', alignItems: 'center', justifyContent: 'center'"
)
app = app.replace(
    "fontSize: '0.8rem',",
    "fontSize: '0.9rem',"
)
app = app.replace(
    "height: '40px'",
    "height: '48px'"
)

with open("web/src/App.tsx", "w", encoding="utf-8") as f:
    f.write(app)
