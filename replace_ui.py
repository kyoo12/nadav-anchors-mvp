with open("web/src/App.tsx", "r", encoding="utf-8") as f:
    content = f.read()

import re

pattern = re.compile(r'<motion\.div \s*className="sidebar glass-panel".*?</motion\.div>', re.DOTALL)

new_ui = """<motion.div 
        className="sidebar-container"
        initial={{ x: -400, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
      >
        
        {/* Module A: Header & Actions */}
        <div className="glass-panel" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <div>
              <h1 style={{ fontSize: '2rem', margin: 0, fontWeight: 800 }}>Nadav Anchors</h1>
              <p style={{ margin: 0, color: 'var(--text-muted)' }}>Total Anchors: {anchors.length}</p>
            </div>
            <button 
              onClick={() => setTheme(t => t === 'midnight' ? 'field' : 'midnight')}
              style={{ padding: '12px 16px', borderRadius: '12px', background: 'var(--bg-dark)', border: '1px solid var(--border-glass)', color: 'var(--text-main)', cursor: 'pointer', fontWeight: 600, minHeight: '56px' }}
            >
              {theme === 'midnight' ? '?? Field Mode' : '?? Dark Mode'}
            </button>
          </div>
          
          <form onSubmit={handleSearch} style={{ display: 'flex', gap: '8px' }}>
            <input 
              type="text" 
              placeholder="Search ID (e.g. 104)"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{ flex: 1, padding: '0 16px', borderRadius: '12px', border: '1px solid var(--border-glass)', background: 'var(--bg-dark)', color: 'var(--text-main)', fontSize: '1rem', outline: 'none', minHeight: '56px' }}
            />
            <button type="submit" style={{ padding: '0 24px', background: 'var(--accent-blue)', color: '#fff', border: 'none', borderRadius: '12px', cursor: 'pointer', fontWeight: 600, fontSize: '1rem', minHeight: '56px' }}>
              Find
            </button>
          </form>

          <button 
            onClick={exportCSV}
            style={{ 
              padding: '0 16px', 
              background: 'transparent', 
              border: '2px solid var(--accent-cyan)',
              color: 'var(--accent-cyan)',
              borderRadius: '12px',
              fontSize: '1rem',
              fontWeight: 700,
              cursor: 'pointer',
              minHeight: '56px',
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              gap: '8px'
            }}
          >
            ?? Export Visible CSV
          </button>
        </div>

        <div className="bento-scroll">
          {/* Module B: Floor Filters */}
          <div className="glass-panel">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <h2 style={{ fontSize: '1.25rem', fontWeight: 600, color: 'var(--text-main)', margin: 0 }}>Floors</h2>
              <button 
                onClick={toggleAll}
                style={{ background: 'transparent', color: 'var(--accent-blue)', border: 'none', cursor: 'pointer', fontSize: '1rem', fontWeight: 600, minHeight: '48px', padding: '0 12px' }}
              >
                {visibleFloors.size === floors.length ? 'Hide All' : 'Show All'}
              </button>
            </div>
            <div className="floor-toggles">
              {floors.map(floor => {
                const count = anchors.filter(a => a.floor === floor).length;
                const isActive = visibleFloors.has(floor);
                return (
                  <div 
                    key={floor} 
                    className={`floor-toggle ${isActive ? 'active' : ''}`}
                    onClick={() => toggleFloor(floor)}
                    style={{ minHeight: '56px' }}
                  >
                    <span className="toggle-label">{formatFloor(floor)}</span>
                    <span className="toggle-count">{count}</span>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Module C: Bracket Filters */}
          <div className="glass-panel">
            <h2 style={{ fontSize: '1.25rem', fontWeight: 600, color: 'var(--text-main)', margin: 0, marginBottom: '16px' }}>Bracket Types</h2>
            <div className="floor-toggles">
              {allBracketTypes.map(b => (
                <div 
                  key={b} 
                  className={`floor-toggle ${visibleBrackets.has(b) ? 'active' : ''}`}
                  onClick={() => toggleBracket(b)}
                  style={{ minHeight: '56px' }}
                >
                  <span className="toggle-label">{b}</span>
                  <span className="toggle-count"></span>
                </div>
              ))}
            </div>
          </div>

          {/* Module D: Global Settings */}
          <div className="glass-panel">
            <label style={{ display: 'flex', alignItems: 'center', gap: '16px', cursor: 'pointer', minHeight: '56px', margin: 0, color: 'var(--text-main)' }}>
              <input 
                type="checkbox" 
                checked={showRegularAnchors}
                onChange={(e) => setShowRegularAnchors(e.target.checked)}
                style={{ width: '24px', height: '24px', cursor: 'pointer' }}
              />
              <span style={{ fontSize: '1rem', fontWeight: 500 }}>Show Regular Square Anchors</span>
            </label>
          </div>
        </div>

      </motion.div>"""

new_content = pattern.sub(new_ui, content)

with open("web/src/App.tsx", "w", encoding="utf-8") as f:
    f.write(new_content)
