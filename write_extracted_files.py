"""
Loads the output of the parser (resynced_manifest.json) and extracts
file metadata from each metadata payload. If a filename and extension
are found, writes the trailing binary payload to disk.
"""

import json
import os
import base64
import re

# Load parsed manifest data
with open("output/resynced_manifest.json") as f:
    data = json.load(f)

os.makedirs("output", exist_ok=True)

for unit in data:
    # Get encoded payloads
    b64_payload = unit.get("trailing_b64")
    payload_text = unit.get("payload_b64")
    if not b64_payload or not payload_text:
        continue

    # Decode and extract metadata from metadata payload
    decoded_payload = base64.b64decode(payload_text).decode("utf-8", errors="ignore")
    lines = decoded_payload.splitlines()
    meta = {}
    for line in lines:
        if "/" in line:
            k, v = line.split("/", 1)
            meta[k.strip().lower()] = v.strip()

    # Skip if metadata doesn't contain filename and extension
    if "filename" not in meta or "ext" not in meta:
        print(f"⚠️ Skipping unit {unit.get('_unit')} — missing filename/ext")
        continue

    # Clean and write file
    safe_filename = re.sub(r"[^\w\-\.]", "_", meta["filename"])
    full_path = os.path.join("output", safe_filename)

    try:
        with open(full_path, "wb") as f:
            f.write(base64.b64decode(b64_payload))
        print(f"✅ Saved {safe_filename}")
    except Exception as e:
        print(f"❌ Failed to save {safe_filename}: {e}")
