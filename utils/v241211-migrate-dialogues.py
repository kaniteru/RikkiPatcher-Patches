# Usage: python script.py [Custom patch directory path]

# This script migrates dialogue data generated from versions of RP-v241211 earlier,
# using migration data extracted from the unmodified game generated from RP-v241211 or later,
# to update dialogue data.
#
# Before using this script,
# you must replace the migration folder data to extracted migration data from the game using RP-v241211 or later.

import sys
import os
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def transform_dialogue(patch_dialogue, migr_dialogue):
    transformed = []
    patch_parts = patch_dialogue.split("\n")

    # Add patch dialogues to transformed list with html from migr
    for index, part in enumerate(patch_parts):
        html = migr_dialogue[index]['html'] if index < len(migr_dialogue) else ""
        transformed.append({
            "html": html,
            "text": part
        })

    # Add any remaining dialogues from migr
    for item in migr_dialogue[len(patch_parts):]:
        transformed.append(item)
    
    return transformed

def process_files(patch_dia, migr_dia):
    completed_files = []
    failed_files = []
    total_migrated_dialogues = 0

    for filename in os.listdir(patch_dia):
        if filename.endswith(".json"):
            patch_file_path = os.path.join(patch_dia, filename)
            migr_file_path = os.path.join(migr_dia, filename)
            
            if not os.path.exists(migr_file_path):
                logger.warning(f"Migration file {filename} is missing.")
                failed_files.append(filename)
                continue
            
            try:
                with open(patch_file_path, 'r', encoding='utf-8') as patch_file:
                    patch_data = json.load(patch_file)
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                logger.error(f"Error decoding JSON from patch file {filename}: {e}")
                failed_files.append(filename)
                continue
            
            try:
                with open(migr_file_path, 'r', encoding='utf-8') as migr_file:
                    migr_data = json.load(migr_file)
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                logger.error(f"Error decoding JSON from migration file {filename}: {e}")
                failed_files.append(filename)
                continue

            transformed_data = {}
            file_migrated_dialogues_count = 0
            
            for key, patch_value in patch_data.items():
                if key in migr_data["list"]:
                    # Transform dialogue
                    transformed_data[key] = {
                        "speaker": patch_value["speaker"],
                        "dialogue": transform_dialogue(patch_value["dialogue"], migr_data["list"][key]["dialogue"])
                    }
                    file_migrated_dialogues_count += 1
            
            total_migrated_dialogues += file_migrated_dialogues_count
            
            # Save the transformed data back to the patch file
            try:
                with open(patch_file_path, 'w', encoding='utf-8') as patch_file:
                    json.dump(transformed_data, patch_file, ensure_ascii=False, indent=4)
                completed_files.append(filename)
                logger.info(f"Successfully migrated file {filename} with {file_migrated_dialogues_count} dialogues.")
            except Exception as e:
                logger.error(f"Error writing JSON to patch file {filename}: {e}")
                failed_files.append(filename)

    logger.info(f"Completed migration for {len(completed_files)} files.")
    logger.info(f"Failed migration for {len(failed_files)} files.")
    logger.info(f"Total migrated dialogues: {total_migrated_dialogues}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        logger.error("Usage: python script.py <directory_path>")
        sys.exit(1)
    
    patch = sys.argv[1]
    migr_dia = os.path.join(patch, 'migration', 'dialogues')
    patch_dia = os.path.join(patch, 'dialogues')
    
    process_files(patch_dia, migr_dia)
