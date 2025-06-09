"""
Parses a proprietary .env binary archive format used by HomeVision.

Each unit in the file follows this structure:
1. 8-byte header (nonstandard, logged but ignored)
2. 4-byte little-endian unsigned integer = metadata payload length
3. Metadata payload (UTF-8 text describing the file)
4. 4-byte little-endian trailing length
5. If trailing length > 0, the actual file content of that length

The script extracts each unit and saves a manifest of all payloads to JSON.
"""

import struct
import json
import os
import base64

def read_little_endian_uint32(data, offset):
    """Helper function to read a 4-byte little-endian unsigned int."""
    return struct.unpack_from("<I", data, offset)[0]

def safe_preview(data, limit=80):
    """Returns a short UTF-8 preview of binary data for inspection."""
    try:
        return data.decode("utf-8", errors="ignore")[:limit]
    except Exception:
        return ""

if __name__ == "__main__":
    env_path = "sample.env"
    output_manifest = "output/resynced_manifest.json"
    os.makedirs("output", exist_ok=True)

    with open(env_path, "rb") as f:
        binary = f.read()

    cursor = 0
    unit_count = 0
    units = []

    # Loop through the binary archive sequentially
    while cursor < len(binary):
        if cursor + 12 > len(binary):
            print(f"🛑 Not enough bytes for header + length at offset {cursor}")
            break

        # Step 1: Read 8-byte header and 4-byte metadata length
        data_header = binary[cursor : cursor + 8]
        payload_len = read_little_endian_uint32(binary, cursor + 8)
        print(f"\n🧩 Unit {unit_count}")
        print(f"🔖 Header: {data_header}")
        print(f"📦 Payload Length: {payload_len}")
        cursor += 12

        if cursor + payload_len > len(binary):
            print(f"❌ Payload at {cursor} (len {payload_len}) exceeds file size.")
            break

        # Step 2: Read the metadata payload
        payload = binary[cursor : cursor + payload_len]
        cursor += payload_len

        # Step 3: Read trailing length (file content length)
        if cursor + 4 > len(binary):
            print(f"🛑 Missing trailing length at offset {cursor}")
            break

        trailing_len = read_little_endian_uint32(binary, cursor)
        print(f"📎 Trailing Length: {trailing_len}")
        cursor += 4

        # Step 4: Read file content if present
        trailing_payload = b""
        if trailing_len > 0:
            if cursor + trailing_len > len(binary):
                print(f"❌ Trailing payload at {cursor} (len {trailing_len}) exceeds file size.")
                break
            trailing_payload = binary[cursor : cursor + trailing_len]
            cursor += trailing_len

        # Store both payloads and metadata previews
        units.append({
            "_unit": unit_count,
            "_length": payload_len,
            "_trailing_length": trailing_len,
            "payload_preview": safe_preview(payload),
            "trailing_payload_preview": safe_preview(trailing_payload),
            "payload_b64": base64.b64encode(payload).decode(),
            "trailing_b64": base64.b64encode(trailing_payload).decode(),
        })

        unit_count += 1

    with open(output_manifest, "w") as f:
        json.dump(units, f, indent=2)

    print(f"\n✅ Parsed {unit_count} units. Saved to {output_manifest}")
