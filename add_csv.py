with open("web/src/App.tsx", "r", encoding="utf-8") as f:
    app = f.read()

# Add exportCSV function before the toggleAll function
export_func = """  const exportCSV = () => {
    const visibleAnchors = anchors.filter(a => visibleFloors.has(a.floor));
    const header = "PointID,X,Y,Z,Floor,Type,NearestGridX,OffsetX,NearestGridY,OffsetY,WallGap\n";
    const rows = visibleAnchors.map(a => 
      `${a.id},${a.x.toFixed(3)},${a.y.toFixed(3)},${a.z.toFixed(3)},${a.floor},${a.metadata},${a.nearestGridX},${a.offsetX.toFixed(1)},${a.nearestGridY},${a.offsetY.toFixed(1)},${a.distanceToConcrete.toFixed(1)}`
    ).join("\n");
    
    const blob = new Blob([header + rows], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.setAttribute('hidden', '');
    a.setAttribute('href', url);
    a.setAttribute('download', 'nadav_anchors_export.csv');
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  const toggleAll = () => {"""

app = app.replace("  const toggleAll = () => {", export_func)

# Add the button below the Show Square Anchors checkbox
button_ui = """        <label style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px', fontSize: '1rem', minHeight: '44px', cursor: 'pointer', color: 'var(--text-main)' }}>
          <input type="checkbox" checked={showRegularAnchors} onChange={(e) => setShowRegularAnchors(e.target.checked)} />
          Show Square Anchors
        </label>
        
        <button 
          onClick={exportCSV}
          style={{
            background: 'rgba(0, 240, 255, 0.1)',
            border: '1px solid var(--accent-blue)',
            color: 'var(--text-main)',
            borderRadius: '12px',
            padding: '0 16px',
            marginBottom: '24px',
            cursor: 'pointer',
            fontSize: '1rem',
            minHeight: '48px',
            width: '100%',
            fontWeight: 600,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 0 10px rgba(0, 240, 255, 0.2)'
          }}
        >
          ?? Export Visible CSV
        </button>"""

app = app.replace("""        <label style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px', fontSize: '1rem', minHeight: '44px', cursor: 'pointer', color: 'var(--text-main)' }}>
          <input type="checkbox" checked={showRegularAnchors} onChange={(e) => setShowRegularAnchors(e.target.checked)} />
          Show Square Anchors
        </label>""", button_ui)

with open("web/src/App.tsx", "w", encoding="utf-8") as f:
    f.write(app)
