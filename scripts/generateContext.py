#!/usr/bin/env python3

import argparse
import os
import sys
import datetime # Added for timestamp

# --- Determine Paths Relative to the Script ---
# Gets the absolute path to the directory containing this script.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Defines input and output directories relative to the script's location.
INPUT_DIR = os.path.join(SCRIPT_DIR, '..', 'input') # Go up one level, then into input
OUTPUT_DIR = os.path.join(SCRIPT_DIR, '..', 'output') # Go up one level, then into output

# --- Configuration ---
# Use the absolute paths defined above
GENERIC_INSTRUCTIONS_FILE = os.path.join(INPUT_DIR, "generic-instructions.md")
CONTEXT_FILES_LIST_FILE = os.path.join(INPUT_DIR, "prompt-context-files.txt")
# Output filename will be generated dynamically
# --- End Configuration ---

def get_file_extension(filepath):
    """Gets the file extension without the leading dot."""
    _, ext = os.path.splitext(filepath)
    return ext[1:] if ext else "" # Return extension without '.', or empty string

def read_file_content(filepath):
    """Reads content of a file, returns content or error message."""
    try:
        # Ensure the path exists before trying to open
        if not os.path.exists(filepath):
             return f"Error: File not found at '{filepath}'"
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError: # Keep this just in case, though os.path.exists check helps
        return f"Error: File not found at '{filepath}'"
    except Exception as e:
        return f"Error reading file '{filepath}': {e}"

def main():
    # --- 1. Parse Command Line Arguments ---
    parser = argparse.ArgumentParser(
        description="Generate a Markdown prompt including context from repository files."
    )
    parser.add_argument(
        "--instructions",
        required=True,
        help="The specific request or question for the prompt.",
        metavar='"Your Question/Request"'
    )
    args = parser.parse_args()
    basic_request = args.instructions

    # --- Ensure Output Directory Exists ---
    try:
        os.makedirs(OUTPUT_DIR, exist_ok=True) # exist_ok=True prevents error if dir exists
        print(f"Ensured output directory exists: '{OUTPUT_DIR}'")
    except OSError as e:
        print(f"Error: Could not create output directory '{OUTPUT_DIR}': {e}", file=sys.stderr)
        sys.exit(1)

    # --- Generate Output Filename ---
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    output_filename = f"prompt_{timestamp}.md"
    output_filepath = os.path.join(OUTPUT_DIR, output_filename)
    print(f"Output will be saved to: '{output_filepath}'")


    # --- 2. Read Generic Instructions ---
    print(f"Reading generic instructions from '{GENERIC_INSTRUCTIONS_FILE}'...")
    generic_instructions = read_file_content(GENERIC_INSTRUCTIONS_FILE)
    if generic_instructions.startswith("Error:"):
        print(generic_instructions, file=sys.stderr)
        generic_instructions = "[Could not load generic instructions]" # Placeholder

    # --- 3. Read Context File List ---
    print(f"Reading file list from '{CONTEXT_FILES_LIST_FILE}'...")
    repo_base_path = ""
    relative_file_paths = []
    included_files_list_content = [] # For the bulleted list in output

    try:
        # Check if the context list file exists first
        if not os.path.exists(CONTEXT_FILES_LIST_FILE):
            print(f"Error: Context file list '{CONTEXT_FILES_LIST_FILE}' not found.", file=sys.stderr)
            sys.exit(1)

        with open(CONTEXT_FILES_LIST_FILE, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]
            if not lines:
                print(f"Error: '{CONTEXT_FILES_LIST_FILE}' is empty or only contains comments.", file=sys.stderr)
                sys.exit(1)

            repo_base_path = lines[0]
            relative_file_paths = lines[1:]

            # Use os.path.expanduser to handle ~ in paths if needed
            repo_base_path = os.path.expanduser(repo_base_path)

            if not os.path.isdir(repo_base_path):
                 print(f"Warning: The specified repository base path does not seem to be a valid directory: '{repo_base_path}'", file=sys.stderr)

            if not relative_file_paths:
                 print(f"Warning: No relative file paths listed in '{CONTEXT_FILES_LIST_FILE}' after the base path.", file=sys.stderr)

    except Exception as e: # Catch other potential errors during file processing
        print(f"Error processing '{CONTEXT_FILES_LIST_FILE}': {e}", file=sys.stderr)
        sys.exit(1)

    # --- 4. Read Content of Context Files ---
    print("Reading context files...")
    context_data = [] # List to store tuples of (relative_path, content, extension)
    for rel_path in relative_file_paths:
        # Clean up potential leading/trailing slashes from user input
        clean_rel_path = rel_path.strip R'/\ ' # Remove leading/trailing slashes and whitespace
        full_path = os.path.join(repo_base_path, clean_rel_path)
        print(f"  Processing: {clean_rel_path} (Full: {full_path})")
        content = read_file_content(full_path)
        extension = get_file_extension(clean_rel_path)
        context_data.append((clean_rel_path, content, extension))
        included_files_list_content.append(f"* `{clean_rel_path}`")


    # --- 5. Generate Output Markdown ---
    print(f"Generating output Markdown file '{output_filepath}'...")
    try:
        with open(output_filepath, 'w', encoding='utf-8') as outfile:
            # Basic Request
            outfile.write("# Basic Request\n\n")
            outfile.write(f"{basic_request}\n\n")

            # Generic Instructions
            outfile.write("## Generic Instructions\n\n")
            outfile.write(f"{generic_instructions}\n\n")

            # Context Header
            outfile.write("## Context\n\n")

            # List of Included Files
            outfile.write("### List of Included Files\n\n")
            if included_files_list_content:
                 outfile.write("\n".join(included_files_list_content))
            else:
                 outfile.write("* *No files listed or processed.*")
            outfile.write("\n\n")

            # Individual File Contents
            for rel_path, content, extension in context_data:
                outfile.write(f"#### {rel_path}\n\n")
                outfile.write(f"```{extension}\n")
                outfile.write(f"{content}\n")
                outfile.write("```\n\n")

        print(f"Successfully generated '{output_filepath}'")

    except Exception as e:
        print(f"Error writing output file '{output
