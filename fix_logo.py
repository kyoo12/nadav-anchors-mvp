with open("web/src/App.tsx", "r", encoding="utf-8") as f:
    code = f.read()

old_str = """        <h1>Building Anchors</h1>
        <p>Interactive 3D visualizer. Toggle floors below and click on an anchor for details.</p>"""

new_str = """        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
          <img src="/logo.png" alt="Logo" style={{ height: '40px', objectFit: 'contain' }} />
          <h1 style={{ margin: 0 }}>Building Anchors</h1>
        </div>
        <p>Interactive 3D visualizer. Toggle floors below and click on an anchor for details.</p>"""

code = code.replace(old_str, new_str)

with open("web/src/App.tsx", "w", encoding="utf-8") as f:
    f.write(code)
