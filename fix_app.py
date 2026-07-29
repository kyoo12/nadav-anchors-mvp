with open("web/src/App.tsx", "r", encoding="utf-8") as f:
    code = f.read()

code = code.replace(
    "const [visibleFloors, setVisibleFloors] = useState<Set<number>>(new Set(floors));",
    "const [visibleFloors, setVisibleFloors] = useState<Set<number>>(new Set(floors));\n  const [showRegularAnchors, setShowRegularAnchors] = useState(true);"
)

old_ui = """        <div style={{ marginBottom: '16px', display: 'flex', justifyContent: 'space-between' }}>
          <span style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>
            Showing {anchors.filter(a => visibleFloors.has(a.floor)).length} / {anchors.length}
          </span>
          <button 
            onClick={toggleAll}
            style={{
              background: 'none', border: 'none', color: 'var(--accent-blue)', 
              cursor: 'pointer', fontSize: '0.9rem'
            }}
          >
            {visibleFloors.size === floors.length ? 'Hide All' : 'Show All'}
          </button>
        </div>"""

new_ui = """        <div style={{ marginBottom: '16px', display: 'flex', justifyContent: 'space-between' }}>
          <span style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>
            Showing {anchors.filter(a => visibleFloors.has(a.floor)).length} / {anchors.length}
          </span>
          <button 
            onClick={toggleAll}
            style={{
              background: 'none', border: 'none', color: 'var(--accent-blue)', 
              cursor: 'pointer', fontSize: '0.9rem'
            }}
          >
            {visibleFloors.size === floors.length ? 'Hide All' : 'Show All'}
          </button>
        </div>
        
        <label style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px', fontSize: '0.9rem', cursor: 'pointer', color: 'var(--text-main)' }}>
          <input type="checkbox" checked={showRegularAnchors} onChange={(e) => setShowRegularAnchors(e.target.checked)} />
          Show Square Anchors
        </label>"""

code = code.replace(old_ui, new_ui)

code = code.replace(
    "selectedAnchorId={selectedAnchor?.id || null}",
    "selectedAnchorId={selectedAnchor?.id || null}\n              showRegularAnchors={showRegularAnchors}"
)

with open("web/src/App.tsx", "w", encoding="utf-8") as f:
    f.write(code)


with open("web/src/components/AnchorVisualizer.tsx", "r", encoding="utf-8") as f:
    code = f.read()

code = code.replace(
    "selectedAnchorId: string | null;\n}",
    "selectedAnchorId: string | null;\n  showRegularAnchors?: boolean;\n}"
)

code = code.replace(
    "export default function AnchorVisualizer({ anchors, visibleFloors, onSelectAnchor, selectedAnchorId }: Props) {",
    "export default function AnchorVisualizer({ anchors, visibleFloors, onSelectAnchor, selectedAnchorId, showRegularAnchors = true }: Props) {"
)

code = code.replace(
    "const regularAnchors = useMemo(() => visibleAnchors.filter(a => !a.isMiddleAnchor), [visibleAnchors]);",
    "const regularAnchors = useMemo(() => showRegularAnchors ? visibleAnchors.filter(a => !a.isMiddleAnchor) : [], [visibleAnchors, showRegularAnchors]);"
)

with open("web/src/components/AnchorVisualizer.tsx", "w", encoding="utf-8") as f:
    f.write(code)

