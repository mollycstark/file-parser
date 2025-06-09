from archive_parser import parse_env_file

if __name__ == "__main__":
    # Path to the binary .env file
    env_path = "sample.env"

    with open(env_path, "rb") as f:
        binary_data = f.read()

    # Parse the binary file and extract metadata + files
    file_units = parse_env_file(binary_data)

    # Print summary of extracted files
    print(f"Parsed {len(file_units)} file units.")
    for i, unit in enumerate(file_units):
        print(f"Unit {i}: {unit.get('filename', 'No filename')} ({unit.get('ext', 'No ext')})")
