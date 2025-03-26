import json
import os
import sys
from pathlib import Path


def inject_text_into_json(original_json_path, text_file_path, output_json_path):
    """
    Read text from a text file and inject it back into the original JSON structure.
    Each line in the text file corresponds to a span in the JSON file.
    """
    # Read the original JSON file
    with open(original_json_path, 'r', encoding='utf-8') as file:
        original_data = json.load(file)

    # Read the text file
    with open(text_file_path, 'r', encoding='utf-8') as file:
        text_lines = [line.rstrip('\n') for line in file.readlines()]

    # Convert escaped sequences back to actual escape sequences
    text_lines = [line.replace('\\n', '\n').replace('\\r', '\r').replace('\\t', '\t') for line in text_lines]

    # Inject text back into the JSON structure
    line_index = 0

    # Function to update spans in an entry
    def update_spans(spans):
        nonlocal line_index
        for span in spans:
            if 'text' in span and line_index < len(text_lines):
                span['text'] = text_lines[line_index]
                line_index += 1

    # Check if data is a dictionary with numbered keys
    if isinstance(original_data, dict) and all(k.isdigit() for k in original_data.keys() if k):
        # Process each entry
        entries = sorted(original_data.items(), key=lambda x: int(x[0]) if x[0].isdigit() else float('inf'))
        for _, entry in entries:
            if 'spans' in entry:
                update_spans(entry['spans'])
    # If data has direct spans array
    elif isinstance(original_data, dict) and 'spans' in original_data:
        update_spans(original_data['spans'])

    # Make sure the output directory exists
    os.makedirs(os.path.dirname(output_json_path), exist_ok=True)

    # Save the updated JSON
    with open(output_json_path, 'w', encoding='utf-8') as file:
        json.dump(original_data, file, ensure_ascii=False, indent=4)

    print(f"Updated JSON saved to {output_json_path}")


def process_files(original_json_dir, text_dir, output_dir):
    """
    Process corresponding JSON and text files in the input directories.
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Get all JSON files in the original JSON directory
    json_files = list(Path(original_json_dir).glob('*.json'))

    if not json_files:
        print(f"No JSON files found in {original_json_dir}")
        return

    for json_file in json_files:
        base_name = json_file.stem
        text_file_path = os.path.join(text_dir, f"{base_name}.txt")

        if not os.path.exists(text_file_path):
            print(f"Warning: No corresponding text file found for {json_file.name}")
            continue

        output_json_path = os.path.join(output_dir, json_file.name)
        inject_text_into_json(str(json_file), text_file_path, output_json_path)


def main():
    if len(sys.argv) != 4:
        print("Usage: python script.py <original_json_dir> <text_dir> <output_dir>")
        sys.exit(1)

    original_json_dir = sys.argv[1]
    text_dir = sys.argv[2]
    output_dir = sys.argv[3]

    if not os.path.exists(original_json_dir):
        print(f"Original JSON directory {original_json_dir} does not exist")
        sys.exit(1)

    if not os.path.exists(text_dir):
        print(f"Text directory {text_dir} does not exist")
        sys.exit(1)

    process_files(original_json_dir, text_dir, output_dir)


if __name__ == "__main__":
    main()
