import ezdxf
from ezdxf.tools.text import plain_text

doc = ezdxf.readfile('TopVue0-R.dxf')
mapping = {}

for block in doc.blocks:
    if block.name.startswith('*'): continue
    texts = list(block.query('TEXT MTEXT'))
    if texts:
        t = texts[0]
        val = t.dxf.text if t.dxftype() == 'TEXT' else plain_text(t.text)
        mapping[block.name] = val.strip()

print("DXF Block to Text Mapping:")
for k, v in mapping.items():
    print(f"'{k}': '{v}'")
