import json

with open("web/public/true_anchors.json", "r") as f:
    anchors = json.load(f)

perfect_count = 0
error_count = 0
large_error_count = 0
for a in anchors:
    if a.get('placementErrorAmount', 0) == 0.0:
        perfect_count += 1
    else:
        error_count += 1
        if abs(a['placementErrorAmount']) > 10.0:
            large_error_count += 1

print(f"Total anchors: {len(anchors)}")
print(f"Perfectly placed (0 error): {perfect_count}")
print(f"Has placement error: {error_count}")
print(f"Has large error (>10mm): {large_error_count}")

# Let's print some of the large errors
print("Sample large errors:")
count = 0
for a in anchors:
    if abs(a.get('placementErrorAmount', 0)) > 10.0 and count < 10:
        print(f"Anchor {a['id']} - Metadata: {a['metadata']} - True Dist: {a['distanceToConcrete']:.1f} - Ideal: {a['distanceToConcrete'] - a['placementErrorAmount']} - Error: {a['placementErrorAmount']:.1f}")
        count += 1
