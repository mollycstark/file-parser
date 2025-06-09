# HomeVision .env Archive Parser

This tool parses a proprietary `.env` file format to bundle metadata and embedded files (like images and XML documents). It identifies internal structure, extracts metadata, and writes contained files to disk.

## Features

- Handles variable-length chunks using length-prefixed binary parsing
- Re-syncs automatically when parsing gets off-track
- Outputs a detailed JSON manifest for auditing
- Writes extracted files to the `output/` directory

## Usage
This project requires Python 3.7 or later. It was developed and tested with Python 3.13.2.

### Step 1: Parse the `.env` file
```bash
python3 length_prefixed_parser.py
```
This creates a manifest (`output/resynced_manifest.json`) that includes metadata, text payloads, and embedded binary content.

### Step 2: Extract files to disk
```bash
python3 write_extracted_files.py
```
This reads the manifest and writes each embedded file to the `output/` directory based on the metadata (`filename` and `ext`).

## File Structure

- `length_prefixed_parser.py`: Parses the binary file and creates a manifest.
- `write_extracted_files.py`: Writes embedded files to disk using the manifest.
- `output/`: Contains extracted files and the manifest.

## Notes

- Designed specifically for the `sample.env` format provided.
- Robust against malformed chunks and misaligned data.
