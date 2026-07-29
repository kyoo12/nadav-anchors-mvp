with open("web/src/App.tsx", "r", encoding="utf-8") as f:
    app = f.read()

app = app.replace(
    "style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px', fontSize: '1rem', minHeight: '44px', minWidth: '44px', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer', color: 'var(--text-main)' }}",
    "style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px', fontSize: '1rem', minHeight: '44px', cursor: 'pointer', color: 'var(--text-main)' }}"
)

with open("web/src/App.tsx", "w", encoding="utf-8") as f:
    f.write(app)
