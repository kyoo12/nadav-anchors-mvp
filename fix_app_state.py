with open("web/src/App.tsx", "r", encoding="utf-8") as f:
    code = f.read()

code = code.replace(
    "const [visibleFloors, setVisibleFloors] = useState<Set<number>>(new Set());",
    "const [visibleFloors, setVisibleFloors] = useState<Set<number>>(new Set());\n  const [showRegularAnchors, setShowRegularAnchors] = useState(true);"
)

with open("web/src/App.tsx", "w", encoding="utf-8") as f:
    f.write(code)
