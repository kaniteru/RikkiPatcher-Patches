import json
import os
import sys
from pathlib import Path


def extract_spans_from_json(json_file_path, output_dir):
    """
    Extract text from spans in the JSON file and write to a text file.
    Each span is written on its own line.
    Escape sequences are preserved literally.
    """
    # Read JSON file
    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Create output file name with the same base name as the input file
    output_file_path = os.path.join(output_dir, os.path.basename(json_file_path).replace('.json', '.txt'))

    # Extract spans and write each one to a separate line
    with open(output_file_path, 'w', encoding='utf-8') as out_file:
        # Function to process spans from an entry
        def process_spans(spans):
            for span in spans:
                if 'text' in span:
                    # Preserve escape sequences by replacing actual ones with their literal representation
                    text = span['text']
                    escaped_text = text.replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
                    out_file.write(escaped_text + '\n')  # Add a newline after each span

        # Check if data is a dictionary with numbered keys
        if isinstance(data, dict) and all(k.isdigit() for k in data.keys() if k):
            # Process each entry
            entries = sorted(data.items(), key=lambda x: int(x[0]) if x[0].isdigit() else float('inf'))
            for _, entry in entries:
                if 'spans' in entry:
                    process_spans(entry['spans'])
        # If data has direct spans array
        elif isinstance(data, dict) and 'spans' in data:
            process_spans(data['spans'])

    print(f"Extracted text from {json_file_path} to {output_file_path}")


def process_directory(input_dir, output_dir):
    """
    Process all JSON files in the input directory.
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Get all JSON files in the input directory
    json_files = list(Path(input_dir).glob('*.json'))

    if not json_files:
        print(f"No JSON files found in {input_dir}")
        return

    for json_file in json_files:
        extract_spans_from_json(str(json_file), output_dir)


def main():
    if len(sys.argv) != 3:
        print("Usage: python script.py <input_directory> <output_directory>")
        sys.exit(1)

    input_dir = sys.argv[1]
    output_dir = sys.argv[2]

    if not os.path.exists(input_dir):
        print(f"Input directory {input_dir} does not exist")
        sys.exit(1)

    process_directory(input_dir, output_dir)


if __name__ == "__main__":
    main()
