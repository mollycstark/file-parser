# parser.py

"""
This module contains logic to parse a proprietary archival .env file
format used by HomeVision. It identifies metadata blocks and extracts
binary file contents based on a repeating delimiter (_SIG/D.C.).
"""

import os, re

# Marker that separates file units
DELIMITER = b"_SIG/D.C."

def parse_env_file(binary_data: bytes):
    """
    Splits the raw binary data on the known delimiter (_SIG/D.C.),
    extracts metadata from each section, and collects info into a list
    of file units (dictionaries).

    Returns:
        List of dicts with extracted metadata and file content (if any)
    """
    raw_units = binary_data.split(DELIMITER)
    file_units = []

    # Iterate over everything except the last unit (no binary after last delimiter)
    for i in range(len(raw_units) - 1):
        metadata_chunk = raw_units[i]
        binary_chunk = raw_units[i + 1]  # content comes *after* delimiter

        # Try decoding metadata
        try:
            decoded = metadata_chunk.decode("utf-8", errors="ignore")
        except Exception as e:
            print(f"Error decoding chunk {i}: {e}")
            continue

        lines = decoded.splitlines()
        metadata = {}
        for line in lines:
            if "/" in line:
                key, val = line.split("/", 1)
                metadata[key.strip().lower()] = val.strip()

        # Save binary file if valid
        if "filename" in metadata and "ext" in metadata:
            safe_filename = re.sub(r"[^\w\-.]", "_", metadata["filename"])
            out_path = os.path.join("output", safe_filename)
            try:
                with open(out_path, "wb") as f:
                    f.write(binary_chunk)
                metadata["saved_to_disk"] = out_path
            except Exception as e:
                print(f"Failed to write {safe_filename}: {e}")
                metadata["write_failed"] = True
        else:
            metadata["metadata_only"] = True

        file_units.append(metadata)

    return file_units
